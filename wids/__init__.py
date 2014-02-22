#!/usr/bin/python

import logging
import flask
import json
import os
import sys
import signal
import time
from xml.etree import ElementTree as ET
from multiprocessing import Pipe, Event, Manager, Lock
from killerbeewids.utils import KBLogUtil, getPlugin
from killerbeewids.drone import DroneClient
from killerbeewids.wids.database import DatabaseHandler
from killerbeewids.wids.server import WIDSWebServer
from killerbeewids.wids.engine import WIDSRuleEngine


class WIDSManager:

	def __init__(self, configfile):
		signal.signal(signal.SIGINT, self.SIGINT)
		self.pid = os.getpid()
		self.desc = 'Daemon'
		self.config = WIDSConfig(configfile)
		#print(self.config.settings)
		self.logutil = KBLogUtil(self.config.settings.get('appname'))
		self.database = DatabaseHandler(self.config.settings.get('database'))
		self.plugins = []
		self.analytics = []
		self.drones = []
		self.processes = []
		self.logutil.logline()
		self.logutil.log(self.desc, 'Initializing', self.pid)
		self.active = True
		self.startWIDS()

	def SIGINT(self, s, f):
		if self.pid == os.getpid():
			print("\n\n[!] SIGINT: Initiating WIDS Shutdown")
			self.logutil.log(self.desc, 'SIGINT', self.pid)
			self.active = False

	def startWIDS(self):
		self.logutil.log(self.desc, 'Starting Daemon', self.pid)
		self.startProcesses()
		self.run()

	def stopWIDS(self):
		self.logutil.log(self.desc, 'Initiating Shutdown', self.pid)
		self.stopProcesses()
		self.logutil.log(self.desc, 'Successfull Shutdown', self.pid)
		print("[!] Succesfully Terminated WIDS")
		self.logutil.endlog()
		sys.exit()

	def startProcesses(self):
		self.startEngine()
		time.sleep(2)
		self.startServer()
		for plugin in self.config.plugins:
			self.startPlugin(plugin)

	def startServer(self):
		self.logutil.log(self.desc, 'Starting Process: WIDSServer', self.pid)
		p = WIDSWebServer(self.config)
		p.start()
		self.processes.append(p)

	def startEngine(self):
		self.logutil.log(self.desc, "Starting Process: WIDSEngine", self.pid)
		p = WIDSRuleEngine(self.config)
		p.start()
		self.processes.append(p)

	def startPlugin(self, plugindata):
		pluginName = plugindata.get('name')
		self.logutil.log(self.desc, 'Starting Process: {0}'.format(pluginName), self.pid)
		pluginClass = getPlugin(plugindata.get('src'))
		pluginProcess = pluginClass(self.config)
		pluginProcess.start()
		self.processes.append(pluginProcess)

	def stopProcesses(self):
		self.logutil.log(self.desc, 'Terminating Child Processes', self.pid)
		for process in self.processes:
			process.terminate()
			process.join()
			self.logutil.log(self.desc, 'Terminated: {0} '.format(process), self.pid)
		self.logutil.log(self.desc, 'Succesfully Terminated Child Processes', self.pid)

	def run(self):
		self.logutil.log(self.desc, 'Starting Main Execution', self.pid)
		while self.active:
			for TaskRequest in self.database.getTaskRequests():
				if TaskRequest.complete == False:
					drone = self.config.drones[0]
					TaskRequest.complete = True
					self.database.session.commit()
					# TODO - add exception handler
					client = DroneClient(drone.get('address'), drone.get('port'))
					client.taskPlugin(TaskRequest.plugin, TaskRequest.channel, TaskRequest.uuid, TaskRequest.parameters)
			time.sleep(5)
		self.logutil.log(self.desc, 'Terminated Main Execution', self.pid)
		self.stopWIDS()

	def processMessage(self, message):
		if message.code == 'task':
			self.taskDrone(message.parameters)

	def manageDrones(self):
		# connect to drones
		pass	
		

	def taskDrone(self, parameters):
		pass

class WIDSConfig:

	def __init__(self, configfile):
		self.settings = {}
		self.plugins = []
		self.rules = []
		self.drones = []
		self.readConfig(configfile)

	def readConfig(self, configfile):
		root = ET.parse(configfile).getroot()
		for settingElement in root.findall('setting'):
			key = settingElement.get('key')
			value = settingElement.get('value')
			self.settings[key] = value
		for pluginElement in root.findall('plugin'):
			plugin = {}
			plugin['src'] = pluginElement.get('src')
			plugin['module'] = pluginElement.get('module')
			plugin['name'] = pluginElement.get('name')
			parameters = {}
			for parameterElement in pluginElement.findall('parameter'):
				parameters[parameterElement.get('key')] = parameterElement.get('value')
			plugin['parameters'] = parameters
			self.plugins.append(plugin)
		for ruleElement in root.findall('rule'):
			pass
		for droneElement in root.findall('drone'):
			drone = {}
			drone['name'] = droneElement.get('name')
			drone['address'] = droneElement.get('address')
			drone['port'] = droneElement.get('port')
			self.drones.append(drone)



