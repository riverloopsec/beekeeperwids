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
from killerbeewids.trunk.utils import KBLogger, RunFile, getPlugin
from killerbeewids.trunk.drone import DroneClient
from killerbeewids.trunk.wids.database import DatabaseHandler
from killerbeewids.trunk.wids.server import WIDSWebServer
from killerbeewids.trunk.wids.engine import WIDSRuleEngine



class WIDSManager:

	def __init__(self, configfile):
		self.config = WIDSConfig(configfile)
		print(self.config.settings)
		self.logger = KBLogger(self.config.settings.get('logfile'))
		self.database = DatabaseHandler(self.config.settings.get('database'))
		self.runfile = RunFile('/home/dev/etc/kbwids/app1.run')
		self.plugins = []
		self.drones = []
		self.processes = []
		self.startWIDS()

	def startWIDS(self):
		self.logger.entry("WIDSManager", "Starting WIDS")
		self.runfile.set()
		self.startProcesses()
		self.run()

	def stopWIDS(self):
		self.logger.entry("WIDSManager", "Initiating WIDS Shutdown")
		self.stopProcesses()
		self.runfile.remove()
		self.logger.entry("WIDSManager", "Completed WIDS Shutdown")

	def startProcesses(self):
		self.startServer()
		#self.startEngine()
		for plugin in self.config.plugins:
			pass
			#self.startPlugin(plugin)

	def startServer(self):
		self.logger.entry("WIDSManager", "Starting WIDS WebServer")
		p = WIDSWebServer(self.config)
		p.start()
		self.processes.append(p)

	def startEngine(self):
		self.logger.entry("WIDSManager", "Starting WIDS RuleEngine")
		p = WIDSRuleEngine(self.config)
		p.start()
		self.processes.append(p)

	def startPlugin(self, plugin):
		pluginModule = plugin.get('module')
		pluginName = plugin.get('name')
		pluginParameters = plugin.get('parameters')
		pluginClass = getPlugin('killerbeewids.trunk.wids.plugins.{0}'.format(pluginModule), pluginName)
		pluginProcess = pluginClass(None, None, pluginParameters)
		pluginProcess.start()
		self.processes.append(pluginProcess)
		self.logger.entry("WIDSManager", "Started {0} Plugin".format(pluginProcess))

	def stopProcesses(self):
		self.logger.entry("WIDSManager", "Stoping Child Processes")
		for process in self.processes:
			process.terminate()
			process.join()
			self.logger.entry("WIDSManager", "{0} Terminated".format(process))

	def run(self):
		while self.runfile.check():
			for message in self.database.newMessages():
				print("received a new message")
		self.stopWIDS()
	
	def processMessage(self, message):
		if message.code = 'task':
			self.taskDrone(message.parameters)

	def manageDrones(self):
		# connect to drones
		for drone in self.config.drones:
			
		


	def taskDrone(self, parameters):
		#TODO - task plugin validation
		self.logger.entry("WIDSManager", "Tasking Drone")
		drone = DroneClient()
		drone.		


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
			plugin['module'] = pluginElement.get('module')
			plugin['name'] = pluginElement.get('name')
			parameters = {}
			for parameterElement in pluginElement.findall('parameter'):
				parameters[parameterElement.get('key')] = parameterElement.get('value')
			plugin['parameters'] = parameters
			self.plugins.append(plugin)
		for ruleElement in root.findall('rule'):
			pass




