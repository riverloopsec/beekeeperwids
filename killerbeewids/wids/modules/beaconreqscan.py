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

        self.registerEvent('test', {'channel':15})

        time.sleep(3)
        self.logutil.log('Submitting Drone Task Request')

        #TODO - pull this from settings
        channel = 15

        # Task drones to capture beacon request packets.
        parameters = {'callback': self.config.upload_url,
                      'filter'  : {
                         'fcf': (0x0300, 0x0300),
                         'byteoffset': (7, 0xff, 0x07)
                     }}

        #TODO channel needs to be set dynamically
        uuid_task1 = self.taskDrone(droneIndexList=[0], task_plugin='CapturePlugin', 
                                    task_channel=channel, task_parameters=parameters)

        if uuid_task1 == False:
            self.logutil.log('Failed to Task Drone')
        else:
            self.logutil.log('Successfully tasked Drone with UUID: {0}'.format(uuid_task1))

        # Get packets from database and run statistics
        while self.active:
            datetime_now  = datetime.utcnow()
            datetime_t30  = datetime_now - timedelta(seconds=30)
            datetime_t120 = datetime_now - timedelta(seconds=120)

            n30  = self.getPackets(valueFilterList=[('datetime','>',dateToMicro(datetime_t30))],
                                   uuidFilterList=[uuid_task1], count=True)
            n120 = self.getPackets(valueFilterList=[('datetime','<',dateToMicro(datetime_t30 )),
                                                ('datetime','>',dateToMicro(datetime_t120))],
                                   uuidFilterList=[uuid_task1], count=True)

            an90 = n120/3.0 #30-120 seconds is a 90 second range so 3 * 30sec intervals
            self.logutil.log("debug: Found {0} beacon requests in last 30 seconds, and {1} per 30 secs average over the prior 90 seconds (absolute {2}).".format(n30, an90, n120))
            # Calculate a moving average of how many of these we typically
            #     see in a given time, and if we're significantly higher
            #     than that all of a sudden, we're concerned.
            if n30 > 2 and n30 > (an90*1.5):
                self.logutil.log("alert: Noticed increased beacon requests. (n30={0}, an90={1})".format(n30, an90))

                self.registerEvent(name='IncreasedBeaconRequestDetection', details={'channel':channel, 'n30':n30, 'n120':n120, 'an90':an90})

            # Look for cyclic patterns that indicate a slower scan, perhaps
            #     one is switching across all the channels.
            #TODO

            time.sleep(10)

    def cleanup(self):
        pass

