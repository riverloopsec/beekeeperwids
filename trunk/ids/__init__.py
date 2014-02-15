#!/usr/bin/python


import logging
import flask
import json
import os
import sys
import xml.etree.ElementTree as ET
from multiprocessing import Pipe, Event, Manager, Lock
from data_receiver import DataReceiverProcess
from database import DatabaseHandler
from utils.logger import Logger
from drone import DroneClient
import signal
import time

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


class WIDSManager:
	# this class provides the management logic for the app including:
	# -drone tasking
	# -database management
	# -data listener server
	# -rule engine
	# -process management (analytic plugins)

	def __init__(self, configfile):
		self.config = WIDSConfig(configfile)
		self.logger = Logger(self.config.settings.get('logfile'))
		self.database = DatabaseHandler(self.config.settings.get('database'))
		self.plugins = []
		self.drones = []
		self.processes = []
		self.startWIDS()


	def startWIDS(self):
		self.logger.entry("WIDSManager", "Starting WIDS")
		f = open('/tmp/kbwids.0', 'w')
		f.write('1')
		f.close()
		#self.loadPlugins()
		self.startProcesses()
		self.monitorMessages()

	def stopWIDS(self):
		self.logger.entry("WIDSManager", "Stopping WIDS")
		#self.shutdown = True
		self.stopProcesses()

	def loadPlugins(self):
		# TODO: add error handling for plugins that don't exist
		self.logger.entry('WIDSManager', 'Loading Plugins')
		for plugin in self.config.plugins:
			module = plugin.get('module')
			name = plugin.get('name')
			m = __import__('ids.plugins.{0}'.format(module), fromlist=[name])
			plugin['class'] = getattr(m, name)
			plugin['process'] = None
			self.plugins.append(plugin)

	def startProcesses(self):
		
		self.logger.entry("WIDSManager", "Starting DataReceiver Process")
		process = DataReceiverProcess(None, None, {'port':8888})
		
		process.start()
		self.processes.append(process)

		return
		print("loading plugins")
		for plugin in self.plugins:
			self.logger.entry("WIDSManager", "Starting {0} Plugin".format(plugin.get('name')))
			pluginClass = plugin.get('class')
			pluginParameters = plugin.get('parameters')
			pluginProcess = pluginClass(self.database, self.logger, pluginParameters)
			pluginProcess.start()
			plugin['process'] = pluginProcess

	def stopProcesses(self):
		print("waiting for processes to finish")
		for process in self.processes:
			print(process)
			process.terminate()
			process.join()
			print("process terminated")
		self.shutdown = True
		self.logger.entry("WIDSManager", "Child Processes Terminated")

	def checkRunFile(self):
		f = open('/tmp/kbwids.0', 'r')
		run = f.read()
		f.close()
		if run == '0':
			return False
		else:
			return True

	def monitorMessages(self):
		while self.checkRunFile():
			time.sleep(4)
			print("WIDSManager : {0}".format(os.getpid()))
		self.stopWIDS()

	def taskDrone(self, drone, taskdata):
		pass







