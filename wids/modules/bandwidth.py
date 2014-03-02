#!/usr/bin/python

import time
import signal
import logging
from multiprocessing import Process
from uuid import uuid4
from killerbeewids.wids.modules import AnalyticModule

class BandwidthMonitor(AnalyticModule):
    ''' v0.2
    This is a demonstration application which will alert when the WIDS system
    has stored over N packes in a given timeframe...blah blah blah...
    '''
    def __init__(self, parameters, config):
        AnalyticModule.__init__(self, parameters, config, "BandwidthMonitor")
	self.parameters = parameters
        self.byte_count = 0
        self.packet_count = 0

    def run(self):
	self.configure()
        self.logutil.log('Starting Execution')
	self.running = True

	'''
        # Task drones to capture *ALL* packets.
        parameters = {'callback':self.callbackURL, 'filter':{}}
        uuid = self.taskDrone(plugin='killerbeewids.drone.plugins.capture.CapturePlugin', channel=11, parameters=parameters)
	if uuid == None:
		print("raise exception because failed to task drone")
	'''

        # get packets from database and run statistics
        while self.active:
            pass

	self.logutil.log('Terminating Execution')
	sellf.running = False


    def cleanup(self):
        pass

















