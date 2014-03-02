#!/usr/bin/python

import time
import signal
import logging
from multiprocessing import Process
from uuid import uuid4

import killerbeewids.wids.database as db
from killerbeewids.utils import KBLogUtil
from killerbeewids.wids.plugins import AnalyticPlugin

class BeaconRequestMonitor(AnalyticPlugin):
    '''
    This plugin attempts to detect forged beacon request frames, which could
    be attempting to enumerate the routers/coordinators on the protected
    network. Tools such as KillerBee zbstumbler preform this scan.
    '''
    def __init__(self, config):
        AnalyticPlugin.__init__(self, config, "BeaconRequestMonitor")
        self.desc = 'BeaconRequestMonitor'
        self.byte_count = 0
        self.packet_count = 0
        self.tasks = []

    def run(self):
        self.logutil.log(self.desc, 'Starting Execution', self.pid)

        # Task drones to capture beacon request packets.
        #TODO could taskDrone just return the uuid it picket for the task? We don't need to make them up in the plugins, right?
        uuid = str(uuid4())
        #TODO does callback really need to be in each parameter field, especially hardcoded?
        parameters = {'callback':'http://127.0.0.1:8888/data',
                      'filter'  : {
                         'fcf': (0x0300, 0x0300),
                         'byteoffset': (7, 0xff, 0x07)
                     }}
        #TODO I changed this to channel 15 to see what would happen if the drone got taskings on more channels than interfaces it has...?
        self.taskDrone(uuid, plugin='killerbeewids.drone.plugins.capture.CapturePlugin', channel=15, parameters=parameters)

        # get packets from database and run statistics
        while True:
            #TODO this loop should only select things by UUID from the task/filter entered above
            for packet in self.getNewPackets(self.PACKETS_ALL):
                #TODO our loop will probably switch to running every 30 secs,
                #   either on a timer or using sleep, rather than calling getNewPackets
                print "Found a beacon request packet:", packet.encode('hex')
                # Every N scans, or every time a new "block" of scans occurs,
                #   rasise an "informational level" event.
                #TODO
                
                # Calculate a moving average of how many of these we typically
                #     see in a given time, and if we're significantly higher
                #     than that all of a sudden, we're concerned.
                #TODO query the DB for the number of packets matching our UUID
                #   in the past 30 seconds, and then query the DB for the # of 
                #   packets which were seen between t-30 seconds ago and t-150
                #   seconds ago / 5. Seeing the last 30 seconds higher than the
                #   average of the previous time detects a spike.
		
    def shutdown(self):
        # detask plugin
        pass

    def __generateEvent(self, eventmsg):
        print("Generating Event: {0}".format(eventmsg))


