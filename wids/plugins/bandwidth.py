#!/usr/bin/python

import time
import signal
import logging
from multiprocessing import Process
import killerbeewids.wids.database as db
from killerbeewids.utils import KBLogUtil
from uuid import uuid4

from killerbeewids.wids.plugins import AnalyticPlugin


# TODO - incorporate shutdown event & implement proper shutdown sequence
# TODO - implement proper evenet generation mechanism

class BandwidthMonitor(AnalyticPlugin):

	def __init__(self, config):
		AnalyticPlugin.__init__(self, config, "BandwidthMonitor")
		self.byte_count = 0
		self.packet_count = 0


	def run(self):
		self.logutil.log(self.name, 'Starting Execution', self.pid)
	
		# task drone to capture all packets on ch.11
		# uuid = str(uuid4())
		# parameters = {'callback':'http://127.0.0.1:8888/data', 'filter':{}}
		# self.taskDrone(uuid, plugin='killerbeewids.drone.plugins.capture.CapturePlugin', channel=11, parameters=parameters)

		for packet in self.getNewPackets():
			packet.display()
			self.packet_count += 1
			
		
		if self.packet_count > 10:
			self.generateEvent()	
	
		self.terminate()
	
	
	def shutdown(self):
		pass















