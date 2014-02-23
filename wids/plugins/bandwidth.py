#!/usr/bin/python

import time
import signal
import logging
from multiprocessing import Process
from uuid import uuid4

import AnalyticPlugin

class BandwidthMonitor(AnalyticPlugin):
    ''' v0.2
    This is a demonstration application which will alert when the WIDS system
    has stored over N packes in a given timeframe...blah blah blah...
    '''
    def __init__(self, config):
        AnalyticPlugin.__init__(self, config, "BandwidthMonitor")
        self.desc = 'BandwidthMonitor'
        self.byte_count = 0
        self.packet_count = 0
        self.tasks = []

    def run(self):
        self.logutil.log(self.desc, 'Starting Execution', self.pid)

        # Task drones to capture *ALL* packets.
        uuid = str(uuid4())
        parameters = {'callback':'http://127.0.0.1:8888/data', 'filter':{}}
        self.taskDrone(uuid, plugin='killerbeewids.drone.plugins.capture.CapturePlugin', channel=11, parameters=parameters)

        # get packets from database and run statistics
        while True:
            for packet in self.getNewPackets(self.PACKETS_ALL):
                self.packet_count += 1

            if self.packet_count > 10:
                self.__generateEvent("Reached Packet count!!!!!!")
		
    def shutdown(self):
        # detask plugin
        pass

    def __generateEvent(self, eventmsg):
        print("Generating Event: {0}".format(eventmsg))
















