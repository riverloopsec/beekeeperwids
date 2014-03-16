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

from killerbeewids.utils.errors import ErrorCodes as ec
from killerbeewids.utils import KBLogUtil, microToDate
from killerbeewids.drone.client import DroneClient
from killerbeewids.wids import ModuleContainer, DroneContainer, RuleContainer, TaskContainer, Configuration
from killerbeewids.wids.database import DatabaseHandler, Alert

#TODO - import these dynamically
from killerbeewids.wids.modules.beaconreqscan import BeaconRequestMonitor
from killerbeewids.wids.modules.dissasoc_storm import DisassociationStormMonitor
from killerbeewids.wids.modules.dos_aesctr import DosAesCtrMonitor

class WIDSDaemon:

    def __init__(self, parameters=None, config=None):
        signal.signal(signal.SIGINT, self.SIGINT)
        self.config = WIDSConfig(parameters, config)
        self.config.daemon_pid = os.getpid()
        self.logutil = KBLogUtil(self.config.name, 'Daemon')
        self.database = DatabaseHandler(self.config.name)
        self.engine = None
        self.module_store = {}
        self.module_counter = 0
        self.task_store = {}
        self.task_counter = 0
        self.drone_store = {}
        self.drone_counter = 0

    def SIGINT(self, s, f):
        if self.config.daemon_pid == os.getpid():
            self.logutil.log('SIGINT')
            self.stopDaemon()

    def startDaemon(self):
        self.logutil.writePID()
        self.logutil.startlog()
        self.logutil.log('Starting Daemon')
        self.loadDrones()
        self.loadModules()
        self.startServer()

    def stopDaemon(self):
        self.logutil.log('Initiating Shutdown')
        self.unloadModules()
        self.unloadDrones()
        self.logutil.log('Successfull Shutdown')
        self.logutil.cleanup()
        sys.exit()

    def loadDrones(self):
        count = len(self.config.drones)
        self.logutil.log('Loading Drones (Found {0} Drones in the Config)'.format(count))
        for droneConfig in self.config.drones:
            self.loadDrone(droneConfig)

    def loadDrone(self, droneConfigDict):
        try:
            print(droneConfigDict)
            drone_ip = str(droneConfigDict.get('ip', None))
            drone_port = str(droneConfigDict.get('port', None))
            if drone_ip == None or drone_port == None:
                error = 'Error: Missing Parameter: "address"'
                self.logutil.log(error)
                return self.formatResponse(error, None)
            else:
                droneIndex = self.drone_counter
                droneObject = DroneContainer(droneIndex, drone_ip, drone_port)
                self.drone_store[droneIndex] = droneObject
                self.drone_counter += 1
                self.logutil.log('Loading Drone {0} - {1}:{2}'.format(droneIndex, drone_ip, drone_port))
                return self.formatResponse(None, None)
        except:
            self.handleException()

    def unloadDrones(self):
        self.logutil.log('Unloading Drones')
        self.logutil.log('Found {0} Active Drones'.format(len(self.drone_store)))
        for i in range(len(self.drone_store)):
            self.unloadDrone(i)

    def unloadDrone(self, droneIndexInt):
        try:
            droneObject = self.drone_store.get(droneIndexInt, None)
            if droneObject == None:
                error = 'Error: Drone with Index {0} does not exist'.format(droneIndexInt)
                self.logutil.log(error)
                return self.formatResponse(False, error)
            else:
                droneObject.release()
                self.logutil.log('Releasing Drone {0} - {1}:{2}'.format(droneIndexInt, droneObject.address, droneObject.port))
                del(self.drone_store[droneIndexInt])
                del(droneObject)
                return self.formatResponse(True, None)
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
                module_index = taskConfigDict.get('module_index', None)
                if droneObject == None:
                    error = ec.ERROR_DRONE_InvalidDroneIndex
                    data = droneIndexInt
                    return (error,data)
                if task_uuid == None:
                    error = ec.ERROR_DRONE_MissingDroneTaskParameter
                    data = 'uuid'
                    return (error, data)
                if task_channel == None:
                    error = ec.ERROR_DRONE_MissingDroneTaskParameter
                    data = 'channel'
                    return (error, data)
                if task_plugin == None:
                    error = ec.ERROR_MissingDroneTaskParameter
                    data = 'plugin'
                    return (error, data)
                if task_parameters == None:
                    error = ec.ERROR_MissingDroneTaskParameter
                    data = 'parameters'
                    return (error, data)
                (data,error) = droneObject.api.task(task_plugin, task_channel, task_uuid, task_parameters) 
                if error == None:
                    self.task_store[self.task_counter] = TaskContainer(self.task_counter, task_uuid, task_plugin, task_channel, task_parameters, droneIndexList, module_index)
                    self.task_counter += 1
                return (data,error)
        except:
            self.handleException()


    def detaskDrone(self, droneIndexList, task_uuid):
        try:
            for int_DroneIndex in droneIndexList:
                droneObject = self.drone_store.get(int_DroneIndex, None)
                droneObject.api.detask(task_uuid)
        except Exception:
            self.handleException()


    def loadModules(self):
        count = len(self.config.modules)
        self.logutil.log('Loading Modules (Found {0} Modules in the Config)'.format(count))
        for moduleConfigDict in self.config.modules:
            self.loadModule(moduleConfigDict)
        pass

    def unloadModules(self):
        self.logutil.log('Unloading Modules')
        self.logutil.log('Found {0} Active Modules'.format(len(self.module_store)))
        for i in range(len(self.module_store)):
            self.unloadModule(i)

    def loadModuleClass(self, module):
        if module == 'BeaconRequestMonitor'       : return BeaconRequestMonitor
        if module == 'DisassociationStormMonitor' : return DisassociationStormMonitor
        if module == 'DosAesCtrMonitor'           : return DosAesCtrMonitor

    def loadModule(self, moduleConfigDict):
        self.logutil.debug('Loading Module: {0}'.format(moduleConfigDict))
        try:
            moduleName = moduleConfigDict.get('name', None)
            moduleSettings = moduleConfigDict.get('settings', None)
            moduleClass = self.loadModuleClass(moduleName)
            if moduleName == None:
                error = ec.ERROR_WIDS_MissingModuleParameter
                data = 'name'
                self.logutil.log('Failed to Load Module - Missing Parameter: "name" in {0}\n'.format(moduleConfigDict))
                return self.formatResponse(error,data)
            elif moduleSettings == None:
                error = ec.ERROR_WIDS_MissingModuleParameter
                data = 'settings'
                self.logutil.log('Failed to Load Module - Missing Parameter: "settings" in {0}\n'.format(moduleConfigDict))
                return self.formatResponse(error,data)
            elif moduleClass == None:
                error = ec.ERROR_WIDS_MissingModuleClass
                data = moduleName
                self.logutil.log('Failed to Load Module - Could not load class: {0}'.format(moduleName))
                return self.formatResponse(error,data)
            else:
                moduleIndex = self.module_counter
                moduleShutdownEvent = Event()
                moduleSettings['module_index'] = moduleIndex
                self.logutil.debug('Found module class: {0}'.format(moduleClass))
                '''
                (error,data) = moduleClass.validate_settings(moduleSettings) 
                if not error == None:
                    return self.formatResponse(error,data)
                '''
                moduleProcess = moduleClass(moduleSettings, self.config, moduleShutdownEvent)
                moduleProcess.start()
                moduleObject = ModuleContainer(moduleIndex, moduleName, moduleSettings, moduleProcess, moduleShutdownEvent)
                self.module_store[moduleIndex] = moduleObject
                self.module_counter += 1
                self.logutil.log('Loading Module {0} - {1}'.format(moduleIndex, moduleObject.name))
                return self.formatResponse(None, None)
        except:
            self.handleException()


    def unloadModule(self, moduleIndexInt):
        try:
            moduleObject = self.module_store.get(moduleIndexInt, None)
            if moduleObject == None:
                error = 'Error: Module with Index {0} does not exist'.format(moduleIndexInt)
                self.logutil.log(error)
                return self.formatResponse(False, error)
            else:
                self.logutil.log('Unloading Module {0} ({1} - {2})'.format(moduleIndexInt, moduleObject.name, moduleObject.process.pid))
                self.logutil.log('Detasking Module Tasks')
                for taskObject in self.task_store.values():
                    if taskObject.module_index == moduleObject.index:
                        drones = taskObject.drones
                        uuid = taskObject.uuid
                        self.logutil.log('Removing Task {0} from Drones {1}'.format(uuid, drones))
                        self.detaskDrone(drones, uuid)
                moduleObject.process.terminate()
                moduleObject.process.join()
                del(self.module_store[moduleIndexInt])
                del(moduleObject)
                return self.formatResponse(True, None)
        except:
            self.handleException()


    def startServer(self):
        self.logutil.log('Starting Server on port {0}'.format(self.config.server_port))
        app = flask.Flask(__name__)
        app.add_url_rule('/active',             None, self.processActiveGetRequest,         methods=['GET'] )
        app.add_url_rule('/status',             None, self.processStatusGetRequest,         methods=['GET'] )
        app.add_url_rule('/data/upload',        None, self.processDataUploadRequest,        methods=['POST'])
        app.add_url_rule('/data/download',      None, self.processDataDownloadRequest,      methods=['POST'])
        app.add_url_rule('/drone/task',         None, self.processDroneTaskRequest,         methods=['POST'])
        app.add_url_rule('/drone/detask',       None, self.processDroneDetaskRequest,       methods=['POST'])
        app.add_url_rule('/drone/add',          None, self.processDroneAddRequest,          methods=['POST'])
        app.add_url_rule('/drone/delete',       None, self.processDroneDeleteRequest,       methods=['POST'])
        app.add_url_rule('/alerts',             None, self.processAlertGetRequest,          methods=['POST'])
        app.add_url_rule('/alerts/generate',    None, self.processAlertGenerateRequest,     methods=['POST'])
        app.add_url_rule('/module/load',        None, self.processModuleLoadRequest,        methods=['POST'])
        app.add_url_rule('/module/unload',      None, self.processModuleUnloadRequest,      methods=['POST'])
        app.run(threaded=True, port=int(self.config.server_port))

    def handleException(self):
        etb = traceback.format_exc()
        self.logutil.trace(etb)
        return self.formatResponse(error=ec.ERROR_GENERAL_UnknownException, data=str(etb))

    def formatResponse(self, error, data):
        return json.dumps({'error':error, 'data':data})

    def processActiveGetRequest(self):
        self.logutil.debug('Processing Active Get Request')
        return self.formatResponse(error=None, data=True)

    def processDataUploadRequest(self):
        self.logutil.debug('Processing Data Upload Request')
        try:
            data = json.loads(flask.request.data)
            packetdata = data.get('pkt')
            self.database.storePacket(packetdata)
            return self.formatResponse(error=None, data=None)
        except Exception:
            return self.handleException()

    def processDataDownloadRequest(self):
        self.logutil.debug('Processing Data Upload Request')
        try:
            return self.formatResponse(error=None, data=None)
        except Exception:
            return self.handleException()

    def processDroneTaskRequest(self):
        self.logutil.debug('Processing Drone Task Request')
        try:
            request_data = json.loads(flask.request.data)
            (error,data) = self.taskDrone(request_data)
            return self.formatResponse(error,data)
        except Exception:
            return self.handleException()

    def processDroneDetaskRequest(self):
        self.logutil.debug('Processing Drone Detask Request')
        try:
            data = json.loads(flask.request.data)
            return self.detaskDrone(data)
        except Exception:
            return self.handleException()

    def processDroneAddRequest(self):
        self.logutil.debug('Processing Drone Add Request')
        try:
            data = json.loads(flask.request.data)
            return self.loadDrone(data)
        except Exception:
            return self.handleException()

    def processDroneDeleteRequest(self):
        self.logutil.debug('Processing Drone Delete Request')
        try:
            data = json.loads(flask.request.data)
            drone_index = int(data.get('drone_index'))
            return self.unloadDrone(drone_index)
        except:
            return self.handleException()

    def processModuleLoadRequest(self):
        self.logutil.debug('Processing Module Load Request')
        try:
            data = json.loads(flask.request.data)
            return self.loadModule(data)
        except:
            return self.handleException()

    def processModuleUnloadRequest(self):
        self.logutil.debug('Processing Module Unload Request')
        try:
            data = json.loads(flask.request.data)
            module_index = int(data.get('module_index'))
            return self.unloadModule(module_index)
        except:
            return self.handleException()

    def processAlertGenerateRequest(self):
        self.logutil.debug('Processing Alert Generate Request')
        try:
            data = json.loads(flask.request.data)
            alert_name = str(data.get('alert_name'))
            self.database.storeAlert(alert_name)
            return self.formatResponse(True, None) 
        except:
            return self.handleException()
        
    def processAlertGetRequest(self):
        #self.logutil.debug('Processing Alert Request')
        try:
            alerts = []
            for alert in self.database.session.query(Alert).all():
                alerts.append('{0} - {1}'.format(microToDate(alert.datetime), alert.name))
            return self.formatResponse(None, alerts)
        except:
            return self.handleException()

    def processStatusGetRequest(self):
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
        self.drones = []
        self.modules = []

    def loadConfig(self, config):
        #TODO load all parameters above from the config file, and call this at startup
        pass

    def json(self):
        return {'name':self.name, 'daemon_pid':self.daemon_pid, 'engine_pid':self.engine_pid, 'server_port':self.server_port}

