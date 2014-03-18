import time, logging
from multiprocessing import Process
from datetime import datetime, timedelta

from beekeeperwids.wids.modules import AnalyticModule
from beekeeperwids.utils import dateToMicro

#TODO rename module
class TemplateMonitor(AnalyticModule):
    '''
    This plugin attempts to detect ____________.
    Tools such as ________ preform this scan.
    '''
    def __init__(self, settings, config, shutdown_event):
        #TODO insert module name
        AnalyticModule.__init__(self, settings, config, shutdown_event, "TemplateMonitor")

    def run(self):
        signal.signal(signal.SIGTERM, self.SIGTERM)
        self.logutil.log('Starting Execution')
        channel = self.settings.get('channel')

        # Check that WIDS server is up before submitting a request
        self.waitForWIDS()
        self.logutil.log('Submitting Drone Task Request')

        # Task drones to capture ___________ packets.
        #TODO customize frontend capture filter
        parameters = {'callback': self.config.upload_url,
                      'filter'  : {
                         'fcf': (0x0300, 0x0300),
                         'byteoffset': (7, 0xff, 0x07)
                     }}

        uuid_task1 = self.taskDrone(droneIndexList=[0], task_plugin='CapturePlugin', 
                                    task_channel=channel, task_parameters=parameters, module_index=self.moduleIndex())
        if uuid_task1 == False:
            self.logutil.log('Failed to Task Drone')
        else:
            self.logutil.log('Successfully tasked Drone with UUID: {0}'.format(uuid_task1))

        # Get packets from database and run statistics
        while not self.shutdown_event.is_set():
            #TODO filter the packets back from the database more, by time, etc as needed
            pkts = self.getPackets(uuidFilterList=[uuid_task1], new=True)
            self.logutil.debug("Found {0} packets since last check.".format(len(pkts)))

            #TODO preform the analytic
            for pkt in pkts:
                spkt = Dot15d4FCS(pkt.pbytes)   # scapify the packet's bytes
                #self.logutil.log("This is an example log message.")
                #TODO publish events or alerts to the database as needed
                self.registerEvent(name='ExampleDetection', 
                                   details={'channel':channel, 'pkt':pkt})

            # This is the (approx) interval at which the database is queried:
            time.sleep(30)

        self.shutdown()

