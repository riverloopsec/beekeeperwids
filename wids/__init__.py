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
from killerbeewids.utils import KBLogUtil, loadModuleClass, DEFAULTCONFIG
from killerbeewids.drone import DroneClient
from killerbeewids.wids.database import DatabaseHandler
from killerbeewids.wids.engine import WIDSRuleEngine



class WIDSDaemon:

	def __init__(self, parameters=None, config=None):
		signal.signal(signal.SIGINT, self.SIGINT)
		self.config = WIDSConfig(parameters, config)
		self.config.daemon_pid = os.getpid()
		self.logutil = KBLogUtil(self.config.name, self.config.workdir, 'Daemon', os.getpid())
		self.database = DatabaseHandler(self.config.name)
		self.engine = None
		self.module_store = []
		self.rule_store = []
		self.task_store = []
		self.drone_store = []

	def SIGINT(self, s, f):
		if self.config.daemon_pid == os.getpid():
			self.logutil.log('SIGINT')
			self.stopDaemon()

	def startDaemon(self):
		print('break A')
		self.logutil.logline()
		self.logutil.log('Starting Daemon')
		self.logutil.writePID()
		print('break B')
		#self.loadDrones()
		#self.loadRules()
		#self.loadModules()
		#self.startEngine()
		self.runServer()

	def stopDaemon(self):
		self.logutil.log('Initiating Shutdown')
		#self.stopEngine()
		#self.unloadModules()
		#self.unloadRules()
		#self.unloadDrones()
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
		self.logutil.log('Loading Drones')
		count = len(self.config.drones)
		self.logutil.log('\tFound {0} Drones in the Config'.format(count))
		for droneConfig in self.config.drones:
			self.loadDrone(droneConfig)

	def loadDrone(self, droneConfigDict):
		try:
			# load config elements, if one is missing, abort
			url = droneConfigDict.get('url', None)
			if url == None:
				self.logutil.log('\tFailed to Load Drone - Missing Parameter: "url" in {0}\n'.format(droneConfigDict))
				return
			droneObject = Drone(url)
			counter = len(self.drone_store)
			self.drone_store.append(droneObject)
			self.logutil.log('\tLoading Drone {0} (URL: {1})'.format(counter, droneObject.url))
		except:
			self.handleException()

	def unloadDrones(self):
		self.logutil.log('Unloading Drones')
		self.logutil.log('\tFound {0} Active Drones'.format(len(self.drone_store)))
		for i in range(len(self.drone_store)):
			self.unloadDrone(i)

	def unloadDrone(self, droneIndexInt):
		try:
			drone = self.drone_store[droneIndexInt]
			self.logutil.log('\tUnloading Drone {0} (ID: {1}, URL: {2})'.format(droneIndexInt, drone.id, drone.url))
			#TODO implement mechanism to send drone signal that realeases it from the WIDS
		except:
			self.handleException()
		
	

	def loadModules(self):
		self.logutil.log('Loading Modules')
		count = len(self.config.modules)
		self.logutil.log('\tFound {0} Modules in the Config'.format(count))
		for moduleConfigDict in self.config.modules:
			self.loadModule(moduleConfigDict)
		pass


	def loadModule(self, moduleConfigDict):
		try:
			# load config elements, if one is missing, abort
			name = moduleConfigDict.get('name', None)
			parameters = moduleConfigDict.get('parameters', None)
			if name == None:
				self.logutil.log('\tFailed to Load Module - Missing Parameter: "name" in {0}\n'.format(moduleConfigDict))
			if parameters == None:
				self.logutil.log('\tFailed to Load Module - Missing Parameter: "parameters" in {0}\n'.format(moduleConfigDict))
				return
			counter = len(self.module_store)
			#moduleClass = loadModuleClass(name)
			#moduleProcess = moduleClass(parameters, self.config)
			#moduleProcess.start()
			#moduleObject = Module(name, parameters, moduleProcess)
			moduleObject = Module(name, parameters, None)
			self.module_store.append(moduleObject)
			self.logutil.log('\tLoading Module {0} ({1})'.format(counter, moduleObject.name))
		except:
			self.handleException()

	def unloadModules(self):
		self.logutil.log('Unloading Modules')
		self.logutil.log('\tFound {0} Active Modules'.format(len(self.module_store)))
		for i in range(len(self.drone_store)):
			self.unloadModule(i)
		

	def unloadModule(self, moduleIndexInt):
		try:
			moduleObject = self.module_store[moduleIndexInt]
			moduleObject.process.shutdown()
			moduleObject.process.join()
			#del(self.module_store[moduleIndexInt])
			self.logutil.log('\tUnloading Module {0} ({1} - {2})'.format(moduleIndexInt, moduleObject.name, moduleObject.process.pid))
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
		print('break C')
		self.logutil.log('Starting Main Execution')
		self.logutil.log('Starting REST Server: http://127.0.0.1:{0}'.format(self.config.server_port))	
		app = flask.Flask(__name__)
		print('break D')
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
		print('break E')
		app.run(threaded=True, port=int(self.config.server_port))
		print('break F')


	def processDataUpload(self, message):
		self.logutil.log('Processing Received Data - from ???')
		try:
			data = json.loads(flask.request.data)
                	packetdata = data.get('pkt')
                	self.database.storePacket(packetdata)
			return "SUCCESS"
		except Exception:
			self.logutil.log('\tFailed to Process Data Upload')
			traceback.print_exc()
			return "FAILURE"


	def processDataDownload(self):
		pass

	def processDroneTask(self):
		pass
		# plugin
		# channel
		# uuid
		# parameters
		# [droneID] or ALL

	def processDroneDetask(self):
		pass
		# uuid
		# [droneID] or ALL

	def processDroneAdd(self):
		pass
		# url

	def processDroneDelete(self):
		pass
		# droneID

	def processModuleLoad(self):
		pass
		# plugin 
		# data

	def processModuleUnload(self):
		pass
		# pluginID

	def processRuleAdd(self):
		pass
		# data

	def processRuleDelete(self):
		pass
		# ruleID

	def processStatusRequest(self):
		self.logutil.log('Processing Task Request')
		try:
			config = self.config.json()
			modules = list((module.json() for module in self.module_store.values()))
			tasks = list((task.json() for task in self.task_store.values()))
			rules = list((rule.json() for rule in self.rule_store.values()))
			drones = list((drone.json() for drone in self.drone_store.values()))
			status = {'config':config, 'modules':modules, 'tasks':tasks, 'drones':drones}
			return json.dumps({'success':True, 'data':status})
		except:
			return self.handleException()	

	def handleException(self):
		etb = traceback.format_exc()
		self.logutil.trace(etb)
		return json.dumps({'success':False, 'data':str(etb)})


class WIDSClient:

	def __init__(self, address, port):
		self.address = address
		self.port = port

	def getStatus(self):
                resource = '/status'
                return self.sendPOST(self.address, self.port, resource, {})

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
                        return None

                try:
                        response_string = response_object.read()
                        return response_string
                except:
			print('failed to read response')
                        return None


class Module:
	def __init__(self, name, parameters, process):
		self.name = name
		self.parameters = parameters
		self.process = process
	def json(self):
		return {'name':self.name, 'parameters':self.parameters, 'process':self.process.pid}

class Drone:
	def __init__(self, url):
		self.url = url
		self.tasks = {}
		self.plugins = {}
		self.id = None
		self.status = None
		self.heartbeat = None
	def json(self):
		return {'id':self.id, 'url':self.url, 'tasks':self.tasks, 'plugins':self.plugins, 'status':self.status, 'heartbeat':self.heartbeat}

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


	def __init__(self, parameters=None, config=None):
		'''
		default config parameters
		'''
		self.name = 'kbwids0'
		self.workdir = '/home/dev/etc/kb'
		self.daemon_pid = None
		self.engine_pid = None
		self.server_port = 8888
		self.server_ip = '127.0.0.1'
		self.upload_url = 'http://{0}:{1}/data/upload'.format(self.server_ip, self.server_ip)
		self.drones = [{'id':'drone11', 'url':'http://127.0.0.1:9999'}]
		self.modules = [{'name':'BandwidthMonitor', 'parameters':{}}]
		
			
	def loadParameters(self, parameters):
		pass

	def loadConfig(self, config):
		pass

	def json(self):
		return {'name':self.name, 'workdir':self.workdir, 'daemon_pid':self.daemon_pid, 'engine_pid':self.engine_pid, 'server_port':self.server_port}



	

