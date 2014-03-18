#!/usr/bin/python

import time
import signal
import logging
from multiprocessing import Process
from uuid import uuid4

from beekeeperwids.wids.modules import AnalyticModule

class BandwidthMonitor(AnalyticModule):
    ''' v0.2
    This is a demonstration application which will alert when the WIDS system
    has stored over N packes in a given timeframe...blah blah blah...
    '''
    def __init__(self, settings, config):
        AnalyticModule.__init__(self, settings, config, "BandwidthMonitor")
        self.byte_count = 0
        self.packet_count = 0

    def run(self):
        self.logutil.log('Starting Execution')
        self.active = True
        self.running = True

        '''
        # Task drones to capture *ALL* packets.
        parameters = {'callback':self.callbackURL, 'filter':{}}
        uuid = self.taskDrone(plugin='beekeeperwids.drone.plugins.capture.CapturePlugin', channel=11, parameters=parameters)
        if uuid == None:
        print("raise exception because failed to task drone")
        '''

        # get packets from database and run statistics
        while self.active:
            pass

        self.logutil.log('Terminating Execution')
        self.running = False

    def cleanup(self):
        pass
