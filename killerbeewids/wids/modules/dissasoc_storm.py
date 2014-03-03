import time
import signal
import logging
from multiprocessing import Process
from time import sleep
from datetime import datetime, timedelta

from scapy.all import Dot15d4FCS, Dot15d4CmdDisassociation, ZigbeeNWKCommandPayload

from killerbeewids.wids.modules import AnalyticModule
from killerbeewids.utils import dateToMicro

class DisassociationStormMonitor(AnalyticModule):
    '''
    This plugin attempts to detect forged beacon request frames, which could
    be attempting to enumerate the routers/coordinators on the protected
    network. Tools such as KillerBee zbstumbler preform this scan.
    '''
    def __init__(self, settings, config):
        AnalyticModule.__init__(self, settings, config, "DisassociationStormMonitor")

    def run(self):
        self.logutil.log('Starting Execution')
        self.active = True

        time.sleep(3)
        self.logutil.log('Submitting Drone Task Request')

        # Task drones to capture beacon request packets.
        # This will collect the IEEE 802.15.4 versions:
        parameters = {'callback': self.config.upload_url,
                      'filter'  : {
                         'fcf': (0x0300, 0x0300),
                         'byteoffset': (7, 0xff, 0x03)
                     }}
        #TODO channel needs to be set dynamically
        uuid_dot15d4 = self.taskDrone(droneIndexList=[0], task_plugin='CapturePlugin', 
                                    task_channel=15, task_parameters=parameters)

        # This will collect the ZigBee version:
        parameters['filter'] = {
                         'fcf': (0x0300, 0x0100), # 802.15.4 type Data
                         #TODO we can't have two byteoffset's currently in the CapturePlugin's filter handler
                         'byteoffset': (9, 0x03, 0x01) #offset within the ZB pkt for Frame Type: Command (0x0001)
                         #'byteoffset': (0x21, 0xff, 0x04) #offset within the ZB pkt for Command Identifier: Leave (0x04)
                     }
        #TODO channel needs to be set dynamically
        uuid_zbnwk = self.taskDrone(droneIndexList=[0], task_plugin='CapturePlugin',
                                    task_channel=15, task_parameters=parameters)

        # Get packets from database and run statistics
        while self.active:
            pkts = self.getPackets(uuidFilterList=[uuid_dot15d4, uuid_zbnwk], new=True)
            self.logutil.log("debug: Found {0} packets since last check.".format(len(pkts)))
            for pkt in pkts:
                self.logutil.log("debug: Got pkt from DB: {0}".format(pkt))
                spkt = Dot15d4FCS(pkt.pbytes)
                if Dot15d4CmdDisassociation in spkt:
                    self.logutil.log("alert: have 802.15.4 Disassociation Frame: {0}.".format(spkt.summary()))
                elif ZigbeeNWKCommandPayload in spkt:
                    self.logutil.log("alert: have ZigbeeNWKCommandPayload Frame: {0}.".format(spkt.summary()))
                else:
                    self.logutil.log("debug: query got us a frame we didn't want: {0}.".format(spkt.summary()))
                #TODO

            time.sleep(15)

    def cleanup(self):
        pass

