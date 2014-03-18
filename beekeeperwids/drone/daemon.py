#!/usr/bin/python

import sys
import plugins
import flask
import argparse
import os
import urllib2, urllib
import threading
import time
import socket
import subprocess
import random
import json
import signal
import traceback
from uuid import uuid4 as generateUUID
from killerbee import kbutils
from beekeeperwids.utils.errors import ErrorCodes as ec
from beekeeperwids.utils import KBLogUtil, KBInterface
from beekeeperwids.drone.plugins.capture import CapturePlugin

class DroneDaemon:

    def __init__(self, name, port):
        signal.signal(signal.SIGINT, self.SIGINT)
        self.port = port
        self.name = name
        self.logutil = KBLogUtil(self.name, 'Daemon', os.getpid())
        self.interfaces = {}
        self.plugins = {}
        self.pid = os.getpid()

    def SIGINT(self, s, f):
        #TODO find a cleaner way to do only handle signals from the parent process ?
        if self.pid == os.getpid():
            self.logutil.log("SIGINT")
            signal.signal(signal.SIGINT, signal.SIG_IGN)
            self.shutdown = True
            self.shutdownDaemon()

    def handleException(self):
        etb = traceback.format_exc()
        print(etb)
        self.logutil.trace(etb)
        return json.dumps({'success':False, 'data':str(etb)})


    def runChecks(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(('', self.port))
            s.close()
        except socket.error:
            print("Error Starting Drone:")
            print("Socket TCP {0} already bound".format(self.port))
            sys.exit()

    def startDaemon(self):
        self.runChecks()
        self.logutil.writePID()
        self.logutil.startlog()
        self.logutil.log("Starting DroneDaemon")
        self.enumerateInterfaces()
        self.startRestServer()

    def shutdownDaemon(self):
        self.logutil.log('Initiating shutdown')
        self.stopRunningPlugins()
        self.logutil.log('Completed shutdown')
        self.logutil.cleanup()
        # TODO: verify that all subprocess have been terminated
        sys.exit()

    def startRestServer(self):
        self.logutil.log('Starting REST Server on port {0}'.format(self.port))
        app = flask.Flask(__name__)
        app.add_url_rule('/task',       None, self.processTaskRequest,          methods=['POST'])
        app.add_url_rule('/detask',     None, self.processDetaskRequest,        methods=['POST'])
        app.add_url_rule('/status',     None, self.processStatusGetRequest,     methods=['POST'])
        app.run(port=self.port, threaded=True)

    def handleUnknownException(self):
        etb = traceback.format_exc()
        self.logutil.trace(etb)
        return self.formatResult(error=ec.ERROR_UnknownException, data=str(etb))

    def formatResponse(self, error, data):
        return json.dumps({'error':error, 'data':data})

    def processTaskRequest(self):
        self.logutil.log('Processing Task Request')
        try:
            data = json.loads(flask.request.data)
            uuid = data.get('uuid')
            plugin = data.get('plugin')
            channel = data.get('channel')
            parameters = data.get('parameters')
            self.logutil.log('Processing Task Request: {0} ({1})'.format(uuid, plugin))
            (error,data) = self.taskPlugin(plugin, channel, uuid, parameters)
            return self.formatResponse(error,data)
        except Exception:
            return self.handleUnknownException()

    def processDetaskRequest(self):
        self.logutil.log('Processing Detask Request')
        try:
            data = json.loads(flask.request.data)
            uuid = data.get('uuid')
            (error,data) =  self.detaskPlugin(uuid)
            return self.formatResponse(error,None)
        except Exception:
            return self.handleUnknownException()

    def processStatusGetRequest(self):
        self.logutil.log('Processing Status Get Request')
        try:
            status = {}
            status['config'] = {}
            status['config']['pid'] = self.pid
            status['config']['name'] = self.name
            status['interfaces'] = list((interface.info() for interface in self.interfaces.values()))
            status['plugins'] = list((plugin.info() for plugin in self.plugins.values()))
            return self.formatResponse(None, status)
        except Exception:
            self.handleUnknownException()

    def loadPluginClass(self, plugin):
        if plugin == 'CapturePlugin':
            return CapturePlugin

    def taskPlugin(self, plugin, channel, uuid, parameters):
        self.logutil.debug('Tasking Plugin ({0},{1})'.format(plugin,channel))
        pluginObject = self.plugins.get((plugin,channel), None)
        if pluginObject == None:
            self.logutil.log('No Instance of ({0},{1}) Found - Starting New one'.format(plugin, channel))
            (error,data) = self.startPlugin(plugin,channel)
            if error == None:
                pluginObject = data
            else:
                return (error,data)
        try:
            self.logutil.log('Tasking Plugin: ({0}, ch.{1}) with Task {2}'.format(plugin, channel, uuid))
            success = pluginObject.task(uuid, parameters)
            if success == False:
                error = ec.ERROR_DRONE_UnknownTaskingFailure
            else:
                error = None
            return (error,None)
        except Exception:
            self.handleException()

    def startPlugin(self, plugin, channel):
        self.logutil.debug('Starting Plugin ({0},{1})'.format(plugin,channel))
        try:
            interface = self.getAvailableInterface()
            if interface == None:
                self.logutil.log('Failed to Start Plugin - No Avilable Interfaces')
                error = ec.ERROR_DRONE_UnavailableInterface
                return (error, None)
            pluginClass = self.loadPluginClass(plugin)
            if pluginClass == None:
                self.logutil.log('Failed to Start Plugin - Plugin Module: {0} does not exist'.format(plugin))
                error = ec.ERROR_DroneFailedToLoadPlugin
                return (error,plugin)
            self.logutil.log('Acquired Interface: {0}'.format(interface.device))
            self.logutil.log('Loaded Plugin Class: {0}'.format(pluginClass))
            pluginObject = pluginClass([interface], channel, self.name)
            self.plugins[(plugin,channel)] = pluginObject
            self.logutil.log('Successfully Started Plugin')
            time.sleep(0.5)
            error = None
            data = pluginObject
            return (error,data)
        except Exception:
            self.handleException()

    def detaskPlugin(self, uuid):
        self.logutil.log('Processing Detask Request for {0}'.format(uuid))
        try:
            for pluginKey,pluginObject in self.plugins.items():
                for task_uuid in pluginObject.tasks.keys():
                    if task_uuid == uuid:
                        detask_success = pluginObject.detask(uuid)
                        if detask_success == False:
                            error = ec.ERROR_DroneUnknownDetaskingFailure
                            return (error,None)
                        time.sleep(2)
                        if pluginObject.active == False:
                            del(self.plugins[pluginKey])
                        self.logutil.log('Succesfully detasked {0} from {1}'.format(uuid, str(pluginObject.desc)))
                        return (None,None)
        except Exception:
            return self.handleException()

    def stopRunningPlugins(self):
        self.logutil.log('Stopping Running Plugins')
        for plugin in self.plugins.values():
            if plugin.active == True:
                self.logutil.log("Stopping Plugin: {0}".format(plugin.desc))
                plugin.shutdown()
                if plugin.active:
                    print("had a problem shutting down plugin")
        self.logutil.log('Running plugins have been terminated')

    def getAvailableInterface(self):
        for interface in self.interfaces.values():
            if not interface.active:
                return interface
        return None

    def enumerateInterfaces(self):
        self.logutil.log("Enumerating Interfaces")
        try:
            for interface in kbutils.devlist():
                device = interface[0]
                description = interface[1]
                self.logutil.log("Added new interface: {0}".format(device))
                self.interfaces[device] = KBInterface(device)
        except Exception:
            self.handleUnknownException()



