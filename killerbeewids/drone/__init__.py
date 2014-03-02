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
from killerbeewids.utils import KBLogUtil, KBInterface
from plugins import capture

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
        if self.logutil.checkRunFile():
            pid = self.runfile.pid()
            print("Error Starting Drone:")
            print("Run file for drone already exists: {0}".format(self.runfile.runfile))
            print("Please ensure process: {0} is not running, and remove files manually".format(pid))
            sys.exit()

    def startDaemon(self):
        self.runChecks()
        self.logutil.logline()
        self.logutil.log("Starting DroneDaemon")
        self.logutil.writePID()
        self.enumerateInterfaces()
        self.startRestServer()

    def shutdownDaemon(self):
        self.logutil.log('Initiating shutdown')
        self.stopRunningPlugins()
        self.logutil.log('Completed shutdown')
        self.logutil.endlog()
        self.logutil.deletePID()
        # TODO: verify that all subprocess have been terminated
        sys.exit()

    def processShutdownRequest(self):
        pass

    def startRestServer(self):
        self.logutil.log('Starting REST Server: http://*:{0}'.format(self.port))
        app = flask.Flask(__name__)
        app.add_url_rule('/shutdown', None, self.shutdownDaemon, methods=['POST'])
        app.add_url_rule('/task', None, self.processTaskRequest, methods=['POST'])
        app.add_url_rule('/detask', None, self.processDetaskRequest, methods=['POST'])
        app.add_url_rule('/status', None, self.status, methods=['POST'])
        app.run(port=self.port, threaded=True)

    def processTaskRequest(self):
        try:
            data = json.loads(flask.request.data)
            uuid = data.get('uuid')
            plugin = data.get('plugin')
            channel = data.get('channel')
            parameters = data.get('parameters')
            self.logutil.log('Processing Task Request: {0} ({1})'.format(uuid, plugin))
            return self.taskPlugin(plugin, channel, uuid, parameters)
        except:
            return self.handleException()

    def taskPlugin(self, plugin, channel, uuid, parameters):
        pluginObject = self.plugins.get((plugin,channel), None)
        if pluginObject == None:
            self.logutil.log('\tNo Instance of ({0},{1}) Found - Starting New one'.format(plugin, channel))

            try:
                # get interface
                interface = self.getAvailableInterface()
                if interface == None:
                    self.logutil.log('\tFailed: No Avilable Interfaces')
                    return {'success':False}
                self.logutil.log('\tAcquired Interface: {0}'.format(interface.device))
                # load class
                pluginClass = loadPluginClass(plugin)
                if pluginClass == None:
                    self.logutil.log('\tFailed: Plugin Module: {0} does not exist'.format(plugin))
                    return {'success':False}
                self.logutil.log('\tLoaded Plugin Class: {0}'.format(pluginClass))
                # start plugin
                pluginObject = pluginClass([interface], channel, self.name)
                self.plugins[(plugin,channel)] = pluginObject
                self.logutil.log('\tInitialized Plugin')
            except Exception:
                self.handleException()


        # task plugin
        try:
            self.logutil.log('Tasking Plugin: ({0}, ch.{1}) with Task {2}'.format(plugin, channel, uuid))
            pluginObject.task(uuid, parameters)
            return json.dumps({'success':True})
        except Exception:
            self.handleException()

        '''
        #TODO -cleanup exception handlers
        # if plugin is not already active on specified channel, start new one
        print(parameters)
        pluginShortName = pluginName.split('.')[-1]
        plugin = self.plugins.get((pluginShortName, channel), None)
        if plugin == None:
                self.logutil.log('\tNo Instance of ({0},{1}) Found - Starting New one'.format(pluginShortName, channel))
                interface = self.getAvailableInterface()
                if interface == None:
                        self.logutil.log('\tFailed: No Avilable Interfaces')
                        return 'FAILED TO TASK PLUGIN - NO AVAILABLE INTERFACES'
                else:
                        self.logutil.log('\tAcquired Interface: {0}'.format(interface.device))
                pluginModule = getPlugin(pluginName)
                if pluginModule == None:
                        return 'FAILED TO TASK PLUGIN - MODULE DOES NOT EXIST'
                else:
                        self.logutil.log('\tLoaded Plugin Module: {0}'.format(pluginModule))
                self.logutil.log('\tStarting Plugin: ({0}, ch.{1})'.format(pluginShortName, channel))

                try:
                        print('break A')
                        print(pluginModule)
                        plugin = pluginModule([interface], channel, self.name)
                        import blahblah
                        print('break B')
                        self.plugins[(pluginShortName, channel)] = plugin
                        print('break C')
                except Exception:
                        self.logutil.log('\tFAILED: Unknown exception: {0}'.format(e))
                        self.handleException()

        # task the plugin
        try:
                self.logutil.log('Tasking Plugin: ({0}, ch.{1}) with Task {2}'.format(pluginShortName, channel, uuid))
                plugin.task(uuid, parameters)
                return "SUCCESS"
        except Exception as e:
                return "FAILED - 2"
        '''


    def processDetaskRequest(self):
        data = json.loads(flask.request.data)
        uuid = data.get('uuid')
        return self.detaskPlugin(uuid)

    def detaskPlugin(self, uuid):
        self.logutil.log('Processing Detask Request for {0}'.format(uuid))
        for pluginKey,pluginObject in self.plugins.items():
            for task_uuid in pluginObject.tasks.keys():
                if task_uuid == uuid:
                    pluginObject.detask(uuid)
                    time.sleep(4)
                    if pluginObject.active == False:
                        del(self.plugins[pluginKey])
                        self.logutil.log('Succesfully detasked {0} from {1}'.format(uuid, str(pluginObject.desc)))
                        return "SUCCESS: DETASKED {0}\n".format(uuid)
                    else:
                        return "FAILURE: COULD NOT DETASK {0}".format(uuid)
        return "FAILURE: COULD NOT FIND TASK {0}\n".format(uuid)

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
        for interface in kbutils.devlist():
            device = interface[0]
            description = interface[1]
            self.logutil.log("\tAdded new interface: {0}".format(device))
            self.interfaces[device] = KBInterface(device)

    def status(self):
        status = {}
        status['config'] = {}
        status['config']['pid'] = self.pid
        status['config']['name'] = self.name
        status['interfaces'] = list((interface.info() for interface in self.interfaces.values()))
        status['plugins'] = list((plugin.info() for plugin in self.plugins.values()))
        return json.dumps(status)



class DroneClient:

    def __init__(self, address, port):
        self.address = address
        self.port = port

    def testTask(self):
        print("running testtask")
        plugin = 'CapturePlugin'
        channel = 15
        uuid = '123456789-d20d-4cb6-970e-85c8ed1cff03'
        parameters = {'callback':'http://127.0.0.1:8888/data', 'filter':{}}
        return self.task(plugin, channel, uuid, parameters)

    def testDetask(self):
        uuid = '813027f9-d20d-4cb6-970e-85c8ed1cff03'
        return self.detaskPlugin(uuid)

    def getStatus(self):
        resource = '/status'
        data = {}
        return self.sendRequest(self.address, self.port, resource, data)

    def getInterfaces(self):
        pass

    def task(self, plugin, channel, uuid, parameters):
        resource = '/task'
        data = {'plugin':plugin, 'channel':channel, 'uuid':uuid, 'parameters':parameters}
        return self.sendRequest(self.address, self.port, resource, data)

    def detask(self, uuid):
        resource = '/detask'
        parameters = {'uuid':uuid}
        return self.sendRequest(self.address, self.port, resource, parameters)

    def shutdownDrone(self):
        resource = '/shutdown'
        parameters = {}
        return self.sendRequest(self.address, self.port, resource, parameters)

    def sendRequest(self, address, port, resource, data):
        url = "http://{0}:{1}{2}".format(address, port, resource)
        http_headers = {'Content-Type' : 'application/json', 'User-Agent' : 'DroneClient'}
        post_data_json = json.dumps(data)
        request_object = urllib2.Request(url, post_data_json, http_headers)
        try:
            response_object = urllib2.urlopen(request_object)
        except:
            return "unable to connect to drone"

        try:
            response_string = response_object.read()
            return response_string
        except:
            return "unable to read response object"

class DroneCodes:
    def __init__(self):
        self.SUCCESS = '0'
        self.TASKPLUGIN_FAILURE_UNAVILABLE_INTERFACES = '1'
