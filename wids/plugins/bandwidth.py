#!/usr/bin/python

import time
import signal
import logging
from multiprocessing import Process
import killerbeewids.wids.database as db
from killerbeewids.utils import KBLogUtil
from uuid import uuid4


class AnalyticPlugin(Process):

	def __init__(self, config, name):
		Process.__init__(self)
		self.name = name
		self.config = config
		self.desc = None
		self.logutil = KBLogUtil(self.config.settings.get('appname'))
		self.database = db.DatabaseHandler(self.config.settings.get('database'))


	def taskDrone(self, uuid, plugin, channel, parameters):
		pass

	def detaskDrone(self, uuid, plugin, channel, parameters):
		pass

	def getPackets(self):
		pass

	def getEvents(self):
		pass

	def registerEvent(self):
		pass


	def run(self):
		'''
		overwrite this method
		'''
		pass


	def shutdown(self):
		'''
		overwrite this methods
		'''
		pass



# TODO - incorporate shutdown event & implement proper shutdown sequence
# TODO - implement proper evenet generation mechanism

class BandwidthMonitor(AnalyticPlugin):

	def __init__(self, config):
		AnalyticPlugin.__init__(self, config, "BandwidthMonitor")
		self.desc = 'BandwidthMonitor'
		self.byte_count = 0
		self.packet_count = 0
		self.tasks = []

	def run(self):
		self.logutil.log(self.desc, 'Starting Execution', self.pid)
	
		# task drone to capture all packets on ch.11
		uuid = str(uuid4())
		plugin = 'killerbeewids.drone.plugins.capture.CapturePlugin'
		channel = 11
		parameters = {'callback':'http://127.0.0.1:8888/data', 'filter':{}}
		self.database.storeTaskRequest(uuid, plugin, channel, parameters)
		time.sleep(5)

		# get packets from database and run statistics
		while True:
			for packet in  self.database.getPackets():
				self.packet_count += 1
				self.database.session.delete(packet)
				self.database.session.commit()
			
			if self.packet_count > 10:
				self.__generateEvent("Reached Packet count!!!!!!")
					
	
	def shutdown(self):
		# detask plugin
		pass

	def __generateEvent(self, eventmsg):
		print("generating event: {0}".format(eventmsg))














