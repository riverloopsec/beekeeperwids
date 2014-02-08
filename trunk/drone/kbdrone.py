#!/usr/bin/python

import sys
from killerbee import kbutils,KillerBee
import plugins
import flask	
import argparse
import os
import urllib2
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
		self.runChecks()
		self.plugins = {}
		self.logger = Logger(self)
		self.daemon_stop = False
		self.interfaces = {}
		self.thread_REST = None
		self.thread_TASK = None
		self.thread_DATA = None
		self.tasks_counter = 0
		self.tasks_completed = {}
		self.tasks_running = {}
		self.tasks_scheduled = []
		self.tasks_catalog = \
		{
			'0x01' : self.task_enumerateInterfaces, 	\
			'0x02' : self.task_capturePackets, 		\
			'0x03' : self.task_replayPackets,		\
		}


	def dummyCall(self):
		task_id = self.task_index()
		task_name = 'task name here'
		task_method = self.dummyFunction
		task_callback = None
		task = Task(task_id, task_name, task_method, task_callback)
		self.task_schedule(task)
		return 'executed dummy call'


	def dummyFunction(self):
		time.sleep(5)	
		print('finished')


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
		self.logger.add('Starting Drone Daemon: {0}'.format(self.drone_id))
		# write run file
		self.logger.add('Writing Run File')
		f = open(self.run_file, 'w')
		f.write('PID={0}\n'.format((os.getpid())))
		f.write('PORT={0}\n'.format(self.port))
		f.close()			
		# load plugins
		self.enumerateInterfaces()
		self.loadPlugins()
		# initialize threads
		self.thread_TASK = threading.Thread(target=self.taskManager)
		self.thread_DATA = threading.Thread(target=self.dataManager)
		self.thread_TASK.start()
		self.thread_DATA.start()
		# start REST server
		self.rest_startServer()
		#m = DroneMonitor()
		#m.start()
		while True:
			a=None

	def stopDaemon(self):
		self.logger.add('Stopping DroneDaemon: {0}'.format(self.drone_id))
		self.daemon_stop = True
		self.thread_TaskManager.join()
		os.remove(self.run_file)
		sys.exit()

	def loadPlugins(self):
		self.logger.add('Loading Plugins'.format(self.drone_id))
		return

	def enumerateInterfaces(self):

		#if self.devtesting = True:
		#	return


		for interface in kbutils.devlist():
			device = interface[0]
			description = interface[1]
			droneContext.interfaces.append(Interface(device, description))


	# the data manager is responsible for monitoring new data and pushing it to the registered url endpoint
	def dataManager(self):
		while not self.daemon_stop:
			time.sleep(10)
	

	def data_store(self):
	# this function is reponsible for storing data generated locally by an active task
		return


	def data_push(self):
	# this function is responsible for pushing data to an external URL endpoint
		return


	def taskManager(self):
		while not self.daemon_stop:

			# monitor scheduled tasks, start task, and move to running tasks
			while len(self.tasks_scheduled) > 0:
				task = self.tasks_scheduled.pop()
				self.task_start(task)

			# monitor running tasks, check if complete, and move to completed tasks
			for task in self.tasks_running.values():
				if not task.thread == None and not task.thread.isAlive():
					self.tasks_completed[task.id] = self.tasks_running.pop(task.id)

			
	def task_index(self):
	# return the current index of tasks (to keep track of how many tasks have run)
		self.tasks_counter += 1
		return self.tasks_counter


	def task_schedule(self, task):
		try:
			self.tasks_scheduled.append(task)
		except e:
			print("schedule task exception")
			print(e)
			sys.exit()

	# launch the task in a new thread and move it to the 'tasks_active' list
	def task_start(self, task):
		try:
			self.logger.add('Starting new task: {0}'.format(task.id))
			task.thread = threading.Thread(target=task.method, name=None, args=(), kwargs={})
			task.thread.start()
			self.tasks_running[task.id] = task
		except e:
			print("start task exception")
			print(e)
			sys.exit()


	def task_stop(self):
		return	


	def task_enumerateInterfaces(self):
		for interface in kbutils.devlist():
			device = interface[0]
			description = interface[1]
			self.interfaces[device] = (Interface(device, description))


	def task_capturePackets(self):
		return


	def task_replayPackets(self):
		return


	def rest_startServer(self):
		app = flask.Flask(__name__)
		app.add_url_rule('/status', None, self.rest_status)
		app.add_url_rule('/interfaces/enumerate', None, self.rest_interfaces_enumerate)
		app.add_url_rule('/daemon/stop', None, self.rest_daemon_stop)
		app.add_url_rule('/dummy', None, self.dummyCall)
		self.thread_REST = threading.Thread(target=app.run, name='REST', args=(), kwargs={'port':self.port})
		self.thread_REST.daemon = True
		self.thread_REST.start()


	def populateStatus(self):
		self.interfaces['/dev/ttyUSB0'] = Interface('/dev/ttyUSB0', 'Apimotev4', 'IDLE')
		self.interfaces['/dev/ttyUSB1'] = Interface('/dev/ttyUSB1', 'Apimotev4', 'IDLE')
		self.tasks_running['1'] = Task('1', 'Enumerate Interface', None, None)
		self.tasks_running['2'] = Task('2', 'CapturePackets', None, None)
		self.tasks_completed['3'] = Task('3', 'CapturePackets', None, None)
		self.tasks_completed['4'] = Task('4', 'ReplayPackets', None, None)

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

	# /status
	def rest_status(self):
		return flask.jsonify(self.getStatus())

	# /interfaces
	def rest_interfaces(self, index):
		if index in ['*', 'all']:
			return self.interfaces

	# /interfaces/enumerate
	def rest_interfaces_enumerate(self):
		self.logger.add('REST Call: /interfaces/enumerate')
		self.task_schedule(Task(self.task_index(), 'Enumerate Interfaces', self.task_enumerateInterfaces, None))
		return 'task scheduled'

	# /tasks
	def rest_tasks(self):
		return

	# /tasks/queu
	def rest_tasks_queu(self):
		return

	# /tasks/active
	def rest_tasks_active(self):
		return

	# /tasks/history
	def rest_tasks_history(self):
		return

	# /tasks/stop/<taskid>
	def rest_tasks_stop(self, taskIndex):
		self.tasks[taskIndex].terminate()

	# /tasks/capturepackets?params?
	def rest_tasks_capturePackets(self, params):
		return

	# /tasks/replaypackets?params?
	def rest_tasks_replaypackets(self, params):
		return

	# /daemon/stop
	def rest_daemon_stop(self):
		print("stopping daemon")
		self.stopDaemon()
		return "stopping daemon..."

	# /daemon/restart
	def rest_daemon_restart(self):
		return






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


class Task:
	def __init__(self, task_id, task_name, method, callback):
		self.id = task_id
		self.runtime = 'now'
		self.name = task_name
		self.callback = callback
		self.method = method
		self.thread = None
	def serialize(self):
		return {'id':str(self.id), 'name':str(self.name), 'callback':str(self.callback), 'method':str(self.method)}










