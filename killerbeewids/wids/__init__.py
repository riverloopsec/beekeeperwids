#!/usr/bin/python

import logging
import flask
import json
import os
import sys
import signal
import time
import urllib2, urllib
import traceback
from collections import OrderedDict
from xml.etree import ElementTree as ET
from multiprocessing import Pipe, Event, Manager, Lock

from killerbeewids.utils import KBLogUtil
from killerbeewids.drone import DroneClient
from killerbeewids.wids.database import DatabaseHandler
from killerbeewids.wids.engine import WIDSRuleEngine
from killerbeewids.wids.modules.beaconreqscan import BeaconRequestMonitor


class WIDSDaemon:

    def __init__(self, parameters=None, config=None):
        signal.signal(signal.SIGINT, self.SIGINT)
        self.config = WIDSConfig(parameters, config)
        self.config.daemon_pid = os.getpid()
        self.logutil = KBLogUtil(self.config.name, 'Daemon', os.getpid())
        self.database = DatabaseHandler(self.config.name)
        self.engine = None
        self.module_store = {}
        self.module_counter = 0
        self.rule_store = {}
        self.rule_counter = 0
        self.task_store = {}
        self.task_counter = 0
        self.drone_store = {}
        self.drone_counter = 0

    def SIGINT(self, s, f):
        if self.config.daemon_pid == os.getpid():
            self.logutil.log('SIGINT')
            self.stopDaemon()

    def startDaemon(self):
        self.logutil.logline()
        self.logutil.log('Starting Daemon')
        self.logutil.writePID()
        self.loadDrones()
        self.loadRules()
        self.loadModules()
        self.startEngine()
        self.runServer()

    def stopDaemon(self):
        self.logutil.log('Initiating Shutdown')
        self.stopEngine()
        self.unloadModules()
        self.unloadRules()
        self.unloadDrones()
        self.logutil.log('Successfull Shutdown')
        self.logutil.endlog()
        self.logutil.deletePID()
        sys.exit()

    def startEngine(self):
        self.logutil.log("Starting Process: WIDSEngine")
        self.engine = WIDSRuleEngine(rules=None)
        self.engine.start()
        self.config.engine_pid = self.engine.pid

    def stopEngine(self):
        self.engine.terminate()
        self.engine.join()
        self.logutil.log('\tTerminated Engine Process')

    def loadDrones(self):
        count = len(self.config.drones)
        self.logutil.log('Loading Drones (Found {0} Drones in the Config)'.format(count))
        for droneConfig in self.config.drones:
            self.loadDrone(droneConfig)

    def loadDrone(self, droneConfigDict):
        try:
            drone_address = str(droneConfigDict.get('address', None))
            drone_port = str(droneConfigDict.get('port', None))
            if drone_address == None or drone_port == None:
                error = 'Error: Missing Parameter: "address"'
                self.logutil.log(error)
                return self.resultMessage(False, error)
            else:
                droneIndex = self.drone_counter
                droneObject = Drone(droneIndex, drone_address, drone_port)
                self.drone_store[droneIndex] = droneObject
                self.drone_counter += 1
                self.logutil.log('\tLoading Drone {0} (URL: {1})'.format(droneIndex, droneObject.url))
                return self.resultMessage(True, None)
        except:
            self.handleException()

    def unloadDrones(self):
        self.logutil.log('Unloading Drones')
        self.logutil.log('\tFound {0} Active Drones'.format(len(self.drone_store)))
        for i in range(len(self.drone_store)):
            self.unloadDrone(i)

    def unloadDrone(self, droneIndexInt):
        try:
            droneObject = self.drone_store.get(droneIndexInt, None)
            if droneObject == None:
                error = 'Error: Drone with Index {0} does not exist'.format(droneIndexInt)
                self.logutil.log(error)
                return self.resultMessage(False, error)
            else:
                droneObject.release()
                self.logutil.log('\tReleasing Drone {0} (URL: {1})'.format(droneIndexInt, droneObject.url))
                del(self.drone_store[droneIndexInt])
                del(droneObject)
                return self.resultMessage(True, None)
        except:
            self.handleException()


    def taskDrone(self, taskConfigDict):
        try:
            droneIndexList = taskConfigDict.get('droneIndexList')
            for droneIndexInt in droneIndexList:
                droneObject = self.drone_store.get(droneIndexInt, None)
                task_uuid = taskConfigDict.get('uuid', None)
                task_plugin = taskConfigDict.get('plugin', None)
                task_channel = taskConfigDict.get('channel', None)
                task_parameters = taskConfigDict.get('parameters', None)
                if droneObject == None or task_uuid == None or task_plugin == None or task_channel == None or task_parameters == None:
                    error = 'Error - missing parameters or drone'
                    self.logutil.log(error)
                    return self.resultMessage(False, error)
                else:
                    return droneObject.client.task(task_plugin, task_channel, task_uuid, task_parameters)
        except:
            self.handleException()


    def loadModules(self):
        count = len(self.config.modules)
        self.logutil.log('Loading Modules (Found {0} Modules in the Config)'.format(count))
        for moduleConfigDict in self.config.modules:
            self.loadModule(moduleConfigDict)
        pass


    def loadModuleClass(self, module):
        if module == 'BeaconRequestMonitor':
            return BeaconRequestMonitor

    def loadModule(self, moduleConfigDict):
        try:
            moduleName = moduleConfigDict.get('name', None)
            moduleSettings = moduleConfigDict.get('settings', None)
            if moduleName == None:
                error = 'Error: Missing Parameters: "name"'
                self.logutil.log(error)
                return self.resultMessage(False, error)
                self.logutil.log('\tFailed to Load Module - Missing Parameter: "name" in {0}\n'.format(moduleConfigDict))
            elif moduleSettings == None:
                error = 'Error: Missing Parameters: "settings"'
                self.logutil.log(error)
                return self.resultMessage(False, error)
            else:
                moduleIndex = self.module_counter
                moduleClass = self.loadModuleClass(moduleName)
                moduleProcess = moduleClass(moduleSettings, self.config)
                moduleProcess.start()
                moduleObject = Module(moduleIndex, moduleName, moduleSettings, moduleProcess)
                self.module_store[moduleIndex] = moduleObject
                self.module_counter += 1
                self.logutil.log('\tLoading Module {0} ({1})'.format(moduleIndex, moduleObject.name))
                return self.resultMessage(True, None)
        except:
            self.handleException()

    def unloadModules(self):
        self.logutil.log('Unloading Modules')
        self.logutil.log('\tFound {0} Active Modules'.format(len(self.module_store)))
        for i in range(len(self.module_store)):
            self.unloadModule(i)

    def unloadModule(self, moduleIndexInt):
        try:
            moduleObject = self.module_store.get(moduleIndexInt, None)
            if moduleObject == None:
                error = 'Error: Module with Index {0} does not exist'.format(moduleIndexInt)
                self.logutil.log(error)
                return self.resultMessage(False, error)
            else:
                self.logutil.log('\tUnloading Module {0} ({1} - {2})'.format(moduleIndexInt, moduleObject.name, moduleObject.process.pid))
                moduleObject.process.shutdown()
                moduleObject.process.join()
                del(self.module_store[moduleIndexInt])
                del(moduleObject)
                return self.resultMessage(True, None)
        except:
            self.handleException()


    def loadRules(self):
        pass

    def unloadRules(self):
        pass

    def loadRule(self):
        pass

    def loadRule(self):
        pass

    def runServer(self):
        self.logutil.log('Starting Main Execution')
        self.logutil.log('Starting REST Server: http://127.0.0.1:{0}'.format(self.config.server_port))
        app = flask.Flask(__name__)
        app.add_url_rule('/status', None, self.processStatusRequest, methods=['POST'])
        app.add_url_rule('/data/upload', None, self.processDataUpload, methods=['POST'])
        app.add_url_rule('/data/download', None, self.processDataDownload, methods=['POST'])
        app.add_url_rule('/drone/task', None, self.processDroneTask, methods=['POST'])
        app.add_url_rule('/drone/detask', None, self.processDroneDetask, methods=['POST'])
        app.add_url_rule('/drone/add', None, self.processDroneAdd, methods=['POST'])
        app.add_url_rule('/drone/delete', None, self.processDroneDelete, methods=['POST'])
        app.add_url_rule('/rule/add', None, self.processRuleAdd, methods=['POST'])
        app.add_url_rule('/rule/delete', None, self.processRuleDelete, methods=['POST'])
        app.add_url_rule('/module/load', None, self.processModuleLoad, methods=['POST'])
        app.add_url_rule('/module/unload', None, self.processModuleUnload, methods=['POST'])
        app.run(threaded=True, port=int(self.config.server_port))

    def resultMessage(self, status, message):
        return json.dumps({'success':status, 'message':message})

    def processDataUpload(self):
        self.logutil.log('Processing Data Upload')
        try:
            data = json.loads(flask.request.data)
            packetdata = data.get('pkt')
            self.database.storePacket(packetdata)
            return json.dumps({'success':True})
        except Exception:
            self.handleException()

    def processDataDownload(self):
        pass

    def processDroneTask(self):
        self.logutil.log('Processing Drone Task Request')
        try:
            data = json.loads(flask.request.data)
            return self.taskDrone(data)
        except:
            return self.handleException()

    def processDroneDetask(self):
        self.logutil.log('Processing Drone Detask Request')
        try:
            data = json.loads(flask.request.data)
            return self.taskDrone(data)
        except:
            return self.handleException()


    def processDroneAdd(self):
        self.logutil.log('Processing Drone Add Request')
        try:
            data = json.loads(flask.request.data)
            return self.loadDrone(data)
        except:
            return self.handleException()

    def processDroneDelete(self):
        self.logutil.log('Processing Drone Delete Request')
        try:
            data = json.loads(flask.request.data)
            drone_index = int(data.get('drone_index'))
            return self.unloadDrone(drone_index)
        except:
            return self.handleException()

    def processModuleLoad(self):
        self.logutil.log('Processing Module Load Request')
        try:
            data = json.loads(flask.request.data)
            return self.loadModule(data)
        except:
            return self.handleException()

    def processModuleUnload(self):
        self.logutil.log('Processing Module Unload Request')
        try:
            data = json.loads(flask.request.data)
            module_index = int(data.get('module_index'))
            return self.unloadModule(module_index)
        except:
            return self.handleException()



    def processRuleAdd(self):
        pass
        # data

    def processRuleDelete(self):
        pass
        # ruleID

    def processStatusRequest(self):
        self.logutil.log('Processing Status Request')
        try:
            config = self.config.json()
            modules = list((module.json() for module in self.module_store.values()))
            tasks = list((task.json() for task in self.task_store.values()))
            rules = list((rule.json() for rule in self.rule_store.values()))
            drones = list((drone.json() for drone in self.drone_store.values()))
            status = {'config':config, 'modules':modules, 'tasks':tasks, 'drones':drones, 'rules':rules}
            return json.dumps({'success':True, 'data':status})
        except:
            return self.handleException()

    def handleException(self):
        etb = traceback.format_exc()
        self.logutil.trace(etb)
        return json.dumps({'success':False, 'data':str(etb)})

'''
class WIDSClient:

    def __init__(self, address, port):
        self.address = address
        self.port = port

    def getStatus(self):
        resource = '/status'
        return self.sendPOST(self.address, self.port, resource, {})

    def addDrone(self, drone_url):
        resource = '/drone/add'
        parameters = {'url':drone_url}
        return self.sendPOST(self.address, self.port, resource, parameters)

    def delDrone(self, drone_index):
        resource = '/drone/delete'
        parameters = {'drone_index':drone_index}
        return self.sendPOST(self.address, self.port, resource, parameters)

    def taskDrone(self, droneIndexList, task_uuid, task_plugin, task_channel, task_parameters):
        resource = '/drone/task'
        parameters = {'droneIndexList':droneIndexList, 'uuid':task_uuid, 'channel':task_channel, 'plugin':task_plugin, 'parameters':task_parameters}
        return self.sendPOST(self.address, self.port, resource, parameters)

    def loadModule(self, name, settings):
        resource = '/module/load'
        parameters = {'name':name, 'settings':settings}
        return self.sendPOST(self.address, self.port, resource, parameters)

    def unloadModule(self, module_index):
        resource = '/module/unload'
        parameters = {'module_index':module_index}
        return self.sendPOST(self.address, self.port, resource, parameters)


    def sendGET(self, address, port, resource):
        pass

    def sendPOST(self, address, port, resource, data):
        url = "http://{0}:{1}{2}".format(address, port, resource)
        http_headers = {'Content-Type' : 'application/json', 'User-Agent' : 'DroneClient'}
        post_data_json = json.dumps(data)
        request_object = urllib2.Request(url, post_data_json, http_headers)
        try:
            response_object = urllib2.urlopen(request_object)
        except:
            print('failed to connect to drone')
            return json.dumps({'success':False, 'data':'Error - could not connect to drone'})

        try:
            response_string = response_object.read()
            return json.dumps({'success':True, 'data':response_string})
        except:
            return json.dumps({'success':False, 'data':'Error - failed to read response from drone'})
'''

class Module:
    def __init__(self, index, name, settings, process):
        self.index = index
        self.name = name
        self.settings = settings
        self.process = process
    def json(self):
        return {'index':self.index, 'name':self.name, 'settings':self.settings, 'process':self.process.pid}

class Drone:
    def __init__(self, index, address, port):
        self.index = index
        self.address = address
        self.port = port
        self.url = 'X'
        self.tasks = {}
        self.plugins = {}
        self.id = None
        self.status = None
        self.heartbeat = None
        self.client = DroneClient(self.address, self.port)
    def release(self):
        #TODO - implement drone release
        pass
    def json(self):
        return {'index':self.index, 'url':self.url, 'tasks':self.tasks, 'plugins':self.plugins, 'status':self.status, 'heartbeat':self.heartbeat}

class Rule:
    def __init__(self, id, conditions, actions):
        self.id = id
        self.conditions = conditions
        self.actions = actions
    def json(self):
        return {'id':self.id, 'conditions':self.conditions, 'action':self.actions}

class Tasks:
    def __init__(self, id, uuid, plugin, channel, callback, parameters):
        self.id = id
        self.uuid = uuid
        self.plugin = plugin
        self.channel = channel
        self.parameters = parameters
    def json(self):
        return {'id':self.id, 'uuid':self.uuid, 'plugin':self.plugin, 'channel':self.channel, 'parameters':self.parameters}


class WIDSConfig:
    '''
    This object represents a config of the WIDS (server/backend) module.
    '''
    def __init__(self, parameters=None, config=None):
        '''
        default config parameters
        '''
        self.name = 'wids0'
        self.daemon_pid = None
        self.engine_pid = None
        self.server_port = 8888
        self.server_ip = '127.0.0.1'
        self.upload_url = 'http://{0}:{1}/data/upload'.format(self.server_ip, self.server_port)
        self.drones = [{'id':'drone11', 'address':'127.0.0.1', 'port':9999}]
        self.modules = [{'name':'BeaconRequestMonitor', 'settings':{}}]

    def loadConfig(self, config):
        #TODO load all parameters above from the config file, and call this at startup
        pass

    def json(self):
        return {'name':self.name, 'daemon_pid':self.daemon_pid, 'engine_pid':self.engine_pid, 'server_port':self.server_port}

