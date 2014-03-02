#!/usr/bin/python

import time
import signal
import logging
from multiprocessing import Process
import killerbeewids.wids.database as db

from killerbeewids.wids.modules import AnalyticModule

class BeaconRequestMonitor(AnalyticModule):
    '''
    This plugin attempts to detect forged beacon request frames, which could
    be attempting to enumerate the routers/coordinators on the protected
    network. Tools such as KillerBee zbstumbler preform this scan.
    '''
    def __init__(self, settings, config):
        AnalyticModule.__init__(self, settings, config, "BeaconRequestMonitor")

    def run(self):
        self.logutil.log('Starting Execution')
        self.active = True

        time.sleep(3)
        self.logutil.log('Submitting Drone Task Request')

        # Task drones to capture beacon request packets.
        #TODO does callback really need to be in each parameter field, especially hardcoded?
        parameters = {'callback': self.config.upload_url,
                      'filter'  : {
                         'fcf': (0x0300, 0x0300),
                         'byteoffset': (7, 0xff, 0x07)
                     }}
        uuid_task1 = self.taskDrone(droneIndexList=[0], task_plugin='CapturePlugin', task_channel=15, task_parameters=parameters)

        # get packets from database and run statistics
        while self.active:
            #TODO this loop should only select things by UUID from the task/filter entered above
            print('Scanning for new packets.')
            #for packet in self.getNewPackets(uuid=[uuid_task1]):
                #TODO our loop will probably switch to running every 30 secs,
                #   either on a timer or using sleep, rather than calling getNewPackets

                #print "Found a beacon request packet:", packet.encode('hex')

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
            time.sleep(5)

    def cleanup(self):
        pass
