#!/usr/bin/python

import signal
import logging
from multiprocessing import Process
from killerbeewids.trunk.wids.database import DatabaseHandler
from killerbeewids.trunk.utils import KBLogger


def generateUUID():

	return 123456


class AnalyticPlugin(Process):

	def __init__(self, config, name):
		Process.__init__(self)
		signal.signal(signal.SIGTERM, self.SIGTERM)	
		self.name = name
		self.config = config
		self.database = DatabaseHandler(self.config.settings.get('database'))
		self.logger = KBLogger(self.config.settings.get('logfile'))
		self.logger.entry(self.name, 'Initializing')

	def SIGTERM(self, sig, frame)
		self.logger.entry(self.name, 'SIGTERM')
		self.shutdown()

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



class BandwidthMonitor(AnalyticPlugin):

	def __init__(self, config):
		Plugin.__init__(self, config, "BandwidthMonitorPlugin")
		self.byte_count = 0

	def run(self):
		# request WIDSManager to task drone to capture data
		uuid = generateUUID()
		parameters = {'channel':11, 'uuid':uuid}
		msg = {'src':'plugin', 'dst':'WIDSManager', 'code':'task:capture', 'parameters':parameters}
		self.database.sendMessage(msg)
		# TODO write execption handler in case that message reply is not succesfull		

		# monitor for new data
		search_parameters = {'tags':['new'], 'uuid':uuid}
		for packet in self.database.getPackets(search_parameters):
			byte_count += packet.byte_size
			if self.checkByteCount():
				return

	def checkByteCount(self):
		if self.byte_count > self.threshold:
			print("Met Threshold!!!!!!!!!!!!!!!!!!!!!")
			#self.widsAPI.registerEvent('met bandwidth threshold')					














