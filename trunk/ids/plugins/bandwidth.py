#!/usr/bin/python


import logging
from multiprocessing import Process


def generateUUID():

	return 123456


class Plugin:

	def __init__(self):
		pass


class BandwidthMonitor(Process):
	'''
	description: this plugins monitors for a BW threshold
	author: RiverloopSecurity,LLC
	'''
	def __init__(self, database, logger, parameters):
		Process.__init__(self)
		self.database = database
		self.logger = logger
		self.parameters = parameters
		self.byte_count = 0

	def run(self):
		print("bandwidth monitor")
		self.logger.entry('BandwidthMonitorPlugin', 'Initializing')

		return

		# request data
		uuid = generateUUID()
		parameters = {'channel':11, 'uuid':uuid}
		#self.widsAPI.requestTask('capture', parameters)
		
		# monitor for new data
		search_parameters = {'tags':['new'], 'uuid':uuid}
		for packet in self.widsAPI.database.getPackets(search_parameters):
			byte_count += packet.byte_size
			if self.checkByteCount():
				return

	def checkByteCount(self):
		if self.byte_count > self.threshold:
			print("Met Threshold!!!!!!!!!!!!!!!!!!!!!")
			#self.widsAPI.registerEvent('met bandwidth threshold')					
