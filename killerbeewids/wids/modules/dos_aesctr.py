import time, logging, signal
from multiprocessing import Process
from datetime import datetime, timedelta

from killerbeewids.wids.modules import AnalyticModule
from killerbeewids.utils import dateToMicro

class DosAesCtrMonitor(AnalyticModule):
    '''
    This plugin attempts to detect ____________.
    Tools such as ________ preform this scan.
    '''
    def __init__(self, settings, config, shutdown_event):
        AnalyticModule.__init__(self, settings, config, shutdown_event, "DosAesCtrMonitor")

    def run(self):
        signal.signal(signal.SIGTERM, self.SIGTERM)
        self.logutil.log('Starting Execution')
        channel = self.settings.get('channel')

        # Check that WIDS server is up before submitting a request
        self.waitForWIDS()
        self.logutil.log('Submitting Drone Task Request')

        # Task drones to capture packets which would cause a denial of service
        # to systems using AES-CTR security mode due to sending a frame counter
        # set to a maximal (or near maximal) value.
        parameters = {'callback': self.config.upload_url,
                      'filter'  : {
                         'fcf': (0x0b00, 0x0900), # fcf_frametype = data && fcf_security = true
                         'byteoffset': (11, 0xff, 0xff) # 090801ffffffff00 000000ff db2d
                     }}

        uuid_task1 = self.taskDrone(droneIndexList=[0], task_plugin='CapturePlugin', 
                                    task_channel=channel, task_parameters=parameters, module_index=self.moduleIndex())
        if uuid_task1 == False:
            self.logutil.log('Failed to Task Drone')
        else:
            self.logutil.log('Successfully tasked Drone with UUID: {0}'.format(uuid_task1))

        # Get packets from database and run statistics
        while not self.shutdown_event.is_set():
            pkts = self.getPackets(uuidFilterList=[uuid_task1], new=True)
            self.logutil.debug("Found {0} packets since last check.".format(len(pkts)))

            for pkt in pkts:
                spkt = Dot15d4FCS(pkt.pbytes)   # scapify the packet's bytes
                if spkt.fcf_security != True:
                    self.logutil.log("Packets are excepted to have 802.15.4 security for this analytic.")
                elif spkt.aux_sec_header.sec_framecounter > 0xFF000000:
                    self.registerEvent(name='HighFrameCounterDetection', 
                                       details={'channel':channel, 'pkt':pkt})

            # This is the (approx) interval at which the database is queried:
            time.sleep(60)

        self.shutdown()

