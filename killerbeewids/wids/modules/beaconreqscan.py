#!/usr/bin/python

import time
import signal
import logging
from multiprocessing import Process
from time import sleep
from datetime import datetime, timedelta

from killerbeewids.wids.modules import AnalyticModule
from killerbeewids.utils import dateToMicro

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
            datetime_now  = datetime.utcnow()
            datetime_t30  = datetime_now - timedelta(seconds=30)
            datetime_t120 = datetime_now - timedelta(seconds=120)
            p30  = self.getPackets(queryFilter=[('datetime','>',dateToMicro(datetime_t30))])
            p120 = self.getPackets(queryFilter=[('datetime','<',dateToMicro(datetime_t30 )),
                                                ('datetime','>',dateToMicro(datetime_t120))])
            n30  = len(p30)
            an90 = len(p120)/3.0 #30-120 seconds is a 90 second range so 3 x 30sec intervals
            self.logutil.log("Found {0} beacon requests in last 30 seconds, and {1} per 30 secs average over the prior 90 seconds.".format(n30, an90))
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
            try:
                ratio = float(n30)/an90
                if ratio > 1.5:
                    self.logutil.log("Noticed increased beacon requests. Ratio {0}.".format(ratio))
            except ZeroDivisonError:
                self.logutil.log("No 30 secs - 120 sec old beacon request data.")
            
            time.sleep(5)

    def cleanup(self):
        pass
