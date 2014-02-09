#!/usr/bin/python

import sys
from killerbee import kbutils,KillerBee
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

class Logger:

	def __init__(self, droneContext):
		self.events = []
		self.output = False
		self.drone_id = droneContext.drone_id
		self.logfile = open('/var/log/kbdrone.{0}.log'.format(self.drone_id), 'w')
		self.add('Initializing log file')
		
	def add(self, msg):
		d = time.strftime("%Y-%m-%d %H:%M:%S")
		entry = '{0} - {1}'.format(d, msg)
		self.logfile.write(entry + '\n')
		self.logfile.flush()
		self.events.append(entry)
		if self.output: print(entry)


class DroneDaemon:

	def __init__(self, drone_id, address='127.0.0.1', port=9999, debug=True):
		self.debug = debug
		self.drone_id = drone_id
		self.run_file = '/var/run/kbdrone.{0}'.format(self.drone_id)
		self.port = port
		self.logger = Logger(self)
		self.daemon_stop = False
		self.interfaces = []
		self.tasks = []

	def runChecks(self):
		# check if port is already bound
		try:		
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.bind(('127.0.0.1', self.port))
			s.close()
		except socket.error:
			print("socket already bound, aborting drone start...")
			sys.exit()
		# check if drone name is already taken & running
		if os.path.isfile(self.run_file):
			print("run file for drone already exists, aborting drone start...")
			sys.exit()

	def startDaemon(self):
		#self.runChecks()
		self.logger.add('Starting Drone Daemon: {0}'.format(self.drone_id))
		self.logger.add('Writing Run File')
		f = open(self.run_file, 'w')
		f.write('PID={0}\n'.format((os.getpid())))
		f.write('PORT={0}\n'.format(self.port))
		f.close()			
		self.enumerateInterfaces()
		self.loadPlugins()
		self.rest_startServer()

	def stopDaemon(self):
		self.logger.add('Stopping DroneDaemon: {0}'.format(self.drone_id))
		self.daemon_stop = True
		self.thread_TaskManager.join()
		os.remove(self.run_file)
		sys.exit()

	def rest_startServer(self):
		app = flask.Flask(__name__)
		app.add_url_rule('/tasks/<plugin>/<uuid>/<channel>/task', None, self.taskPlugin, methods=['POST'])
		app.add_url_rule('/tasks/<plugin>/<uuid>/<channel>/detask', None, self.detaskPlugin, methods=['POST'])
		app.add_url_rule('/test', None, self.test, methods=['GET'])
		app.add_url_rule('/status', None, self.getStatus, methods=['GET'])
		app.run(debug=True, port=self.port)

	def loadPlugins(self):
		self.logger.add('Loading Plugins'.format(self.drone_id))
		self.pluginStore = {'capture' : plugins.capture.CapturePlugin}

	def enumerateInterfaces(self):
		self.interfaces.append(KillerBee('/dev/ttyUSB0'))
		return
		'''
		for interface in kbutils.devlist():
			device = interface[0]
			description = interface[1]
			self.interfaces.append(Interface(device))
		'''

	def getAvailableInterface(self):
		return self.interfaces[0]


	'''
	curl http://127.0.0.1:9999/tasks/capture/00112233/11/task -X POST -H "Content-Type: application/json" -d '{"channel":"1"}'
	'''

	def taskPlugin(self, plugin=None, uuid=None, channel=None):
		interface = self.getAvailableInterface()
		parameters = json.loads(flask.request.data)
		if channel == None:
			return "Missing Parameter: 'channel'"

		pluginInstance = self.pluginStore.get(plugin)([interface], parameters)
		if not pluginInstance.status:
			return "could not instantiate pluginInstance"
		pluginInstance.task(uuid, parameters)		
	
		task = DroneTask(uuid, plugin, channel, parameters, interface, pluginInstance)
		#self.tasks[str(uuid)] = task
		return "successfully started task: {0}".format(uuid)

	def detaskPlugin(self):
		return

	def test(self):
		print(self.app)
		print(flask.request.form)
		print(flask.request.args)
		print(flask.request.values)
		print(flask.request.data)
		return '\nstatus: running\n\n'

	def getStatus(self):
		#self.populateStatus()
		status = {}
		status['config'] = {}
		status['config']['pid'] = os.getpid()
		status['config']['id'] = self.drone_id
		status['interfaces'] = {i.serialize().get('device') : i.serialize() for i in self.interfaces.values()}
		status['tasks_running'] = {t.serialize().get('id') : t.serialize() for t in self.tasks_running.values()}
		status['tasks_completed'] = {t.serialize().get('id') : t.serialize() for t in self.tasks_completed.values()}
		status['event_logs'] = '\n'.join(self.logger.events[-5:])
		print(status)
		return status




class DroneClient:
	
	def __init__(self, address='127.0.0.1', port=9999):
		self.serverAddress = address
		self.serverPort = port
		
	def getStatus(self):
		return self.makeRESTCall('/status')	

	def getInterfaces(self):
		return self.makeRESTCall('/interfaces')

	
		
	def enumerateInterfaces(self):
		return self.makeRESTCall('/interfaces/enumerate')

	def stopDaemon(self):
		return self.makeRESTCall('/daemon/stop')


	def getPlugins(self):
		'''
		determine which plugins the drone has to verify if an app's dependencies are met
		'''
	
	def taskCapture(self, uuid, parameters):
		#task drone to capture packets
		required_plugins = ['capture']
		method = 'POST'
		content = 'application/json'
		headers = { 'Content-Type' : 'application/json' }
		data = {'channel' : 11, 'callback' : 'http:localhost:7777'}
	
		
	def makeHTTPCall(self, resource=None, parameters=None):

		resource = '/tasks/capture/123456/11/task'
		parameters = {'channel':11, 'callback':'http://127.0.0.1:8888/data', 'filter':{}}

		#make a string to hold the url of the request
		url = "http://{0}:{1}{2}".format(self.serverAddress, self.serverPort, resource)
		http_headers = {'Content-Type' : 'application/json', 'User-Agent' : 'DroneClient'}
		post_data_json = json.dumps(parameters)
		request_object = urllib2.Request(url, post_data_json, http_headers)

		response = urllib2.urlopen(request_object)

		#store request response in a string
		html_string = response.read()



	def makeRESTCall(self, path):
		try:
			url = 'http://{0}:{1}{2}'.format(self.serverAddress, self.serverPort, path)
			return urllib2.urlopen(url).read()
		except urllib2.HTTPError, e:
			print "HTTP error: %d" % e.code
		except urllib2.URLError, e:
			print "Network error: %s" % e.reason.args[1]	



class Interface(KillerBee):
	def __init__(self, device, datasource=None, gps=None):
		KillerBee.__init__(self, device, datasource, gps)
		self.task = None


class DroneTask:
	def __init__(self, uuid, plugin, channel, parameters, interface, instance):
		self.uuid = uuid
		self.plugin = plugin
		self.channel = channel
		self.parameters = parameters
		self.interface = interface
		self.state = 'running'
		self.instance = instance










