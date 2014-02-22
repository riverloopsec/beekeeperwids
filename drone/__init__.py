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
from uuid import uuid4 as generateUUID
from killerbee import kbutils
from killerbeewids.utils import KBLogUtil, KBInterface, getPlugin


class DroneDaemon:

	def __init__(self, drone_id, port):
		signal.signal(signal.SIGINT, self.SIGINT)
		self.drone_id = drone_id
		self.port = port
		self.name = 'kbdrone.{0}'.format(self.drone_id)
		self.drone = 'kbdrone.{0}'.format(self.drone_id)
		self.desc = 'DroneDaemon'
		self.logutil = KBLogUtil(self.name)
		self.interfaces = {}
		self.plugins = {}
		self.pid = os.getpid()

	def SIGINT(self, s, f):
		#TODO find a cleaner way to do only handle signals from the parent process ?
		if self.pid == os.getpid():
			self.logutil.log(self.desc, "SIGINT", self.pid)
			signal.signal(signal.SIGINT, signal.SIG_IGN)
			self.shutdown = True
			self.shutdownDaemon()

	def runChecks(self):
		try:		
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.bind(('127.0.0.1', self.port))
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
		self.logutil.log(self.desc, "Starting DroneDaemon", self.pid)
		self.enumerateInterfaces()
		self.startRestServer()

	def shutdownDaemon(self):
		self.logutil.log(self.desc, 'Initiating shutdown', self.pid)
		self.stopRunningPlugins()
		self.logutil.log(self.desc, 'Completed shutdown', self.pid)
		self.logutil.endlog()
		# TODO: verify that all subprocess have been terminated
		sys.exit()

	def processShutdownRequest(self):
		pass

	def startRestServer(self):
		self.logutil.log(self.desc, 'Starting REST Server: http://127.0.0.1:{0}'.format(self.port), self.pid)
		app = flask.Flask(__name__)
		app.add_url_rule('/shutdown', None, self.shutdownDaemon, methods=['POST'])
		app.add_url_rule('/task', None, self.processTaskRequest, methods=['POST'])
		app.add_url_rule('/detask', None, self.processDetaskRequest, methods=['POST'])
		app.add_url_rule('/status', None, self.status, methods=['POST'])
		app.run(port=self.port)

	def processTaskRequest(self):
		data = json.loads(flask.request.data)
		uuid = data.get('uuid')
		pluginName = data.get('plugin')
		pluginShortName = pluginName.split('.')[-1]
		channel = data.get('channel')
		parameters = data.get('parameters')
		self.logutil.log(self.desc, 'Processing Task Request: {0} ({1})'.format(uuid, pluginShortName), self.pid)
		self.taskPlugin(pluginName, channel, uuid, parameters)
		return "PROCESSED REQUEST\n"
		#return "UNABLE TO PROCESS REQUEST: NO AVAILABLE INTERFACES"

	def taskPlugin(self, pluginName, channel, uuid, parameters):
		# if plugin is not already active on specified channel, start new one
		pluginShortName = pluginName.split('.')[-1]
		plugin = self.plugins.get((pluginShortName, channel), None)
		if plugin == None:
			self.logutil.log(self.desc, 'Starting New Plugin: ({0}, ch.{1})'.format(pluginShortName, channel), self.pid)
			# TODO right exception handler for no available interfaces
			interface = self.getAvailableInterface()
			# TODO right exception handler for unablailable plugin
			pluginClass = getPlugin(pluginName)
			plugin = pluginClass([interface], channel, self.drone)
			self.plugins[(pluginShortName, channel)] = plugin
		# task the plugin
		self.logutil.log(self.desc, 'Tasking Plugin: ({0}, ch.{1}) with Task {2}'.format(pluginShortName, channel, uuid), self.pid)
		plugin.task(uuid, parameters)

	def processDetaskRequest(self):
		data = json.loads(flask.request.data)
		uuid = data.get('uuid')
		return self.detaskPlugin(uuid)

	def detaskPlugin(self, uuid):
		self.logutil.log(self.desc, 'Processing Detask Request for {0}'.format(uuid), self.pid)
		for pluginKey,pluginObject in self.plugins.items():
			for task_uuid in pluginObject.tasks.keys():
				if task_uuid == uuid:
					pluginObject.detask(uuid)
					time.sleep(4)
					if pluginObject.active == False:
						del(self.plugins[pluginKey])
						self.logutil.log(self.desc, 'Succesfully detasked {0} from {1}'.format(uuid, str(pluginObject.desc)), self.pid)
						return "SUCCESS: DETASKED {0}\n".format(uuid)
					else:
						return "FAILURE: COULD NOT DETASK {0}".format(uuid)
		return "FAILURE: COULD NOT FIND TASK {0}\n".format(uuid)

	def stopRunningPlugins(self):
		self.logutil.log(self.desc, 'Stopping Running Plugins', self.pid)
		for plugin in self.plugins.values():
			if plugin.active == True:
				self.logutil.log(self.desc, "Stopping Plugin: {0}".format(plugin.desc), self.pid)
				plugin.shutdown()
				if plugin.active:
					print("had a problem shutting down plugin")
		self.logutil.log(self.desc, 'Running plugins have been terminated', self.pid)

	def getAvailableInterface(self):
		for interface in self.interfaces.values():
			if not interface.active:
				return interface
		return None

	def enumerateInterfaces(self):
		self.logutil.log(self.desc, "Enumerating Interfaces", self.pid)
		for interface in kbutils.devlist():
			device = interface[0]
			description = interface[1]
			self.logutil.log(self.desc, "Added new interface: {0}".format(device), self.pid)
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
		plugin = 'killerbeewids.drone.plugins.capture.CapturePlugin'
		channel = 11
		uuid = '813027f9-d20d-4cb6-970e-85c8ed1cff03'
		parameters = {'callback':'http://127.0.0.1:8888/data', 'filter':{}}
		return self.taskPlugin(plugin, channel, uuid, parameters)

	def testDetask(self):
		uuid = '813027f9-d20d-4cb6-970e-85c8ed1cff03'
		return self.detaskPlugin(uuid)

	def getStatus(self):
		resource = '/status'
		data = {}
		return self.sendRequest(self.address, self.port, resource, data)		

	def getInterfaces(self):
		pass

	def taskPlugin(self, pluginName, channel, uuid, parameters):
		resource = '/task'
		data = {'plugin':pluginName, 'channel':channel, 'uuid':uuid, 'parameters':parameters}
		return self.sendRequest(self.address, self.port, resource, data)		

	def detaskPlugin(self, uuid):
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
			response_string = response_object.read()
			return response_string
		except:
			return "unable to connect to drone"












