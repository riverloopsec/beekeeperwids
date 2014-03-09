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
    def __init__(self, settings, config, shutdown_event):
        AnalyticModule.__init__(self, settings, config, shutdown_event, "DisassociationStormMonitor")

    @staticmethod
    def validate_settings(settings):
        '''
        performs validation to ensure the neccessary settings are present
        '''
        required_settings = ['channel', 'module_index']
        for setting in required_settings:
            if not setting in settings.keys():
                error = ec.ERROR_WIDS_MissingModuleSetting
                data = settings
                return (error,data)
        return (None,None)

    def run(self):
        signal.signal(signal.SIGTERM, self.SIGTERM)

        #time.sleep(1)
        self.logutil.log('Starting Execution')
        self.active = True
        channel = self.settings.get('channel')

        # check that WIDS server is up before submitting a request
        self.waitForWIDS()
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
                                    task_channel=channel, task_parameters=parameters, module_index=self.moduleIndex())
        if not uuid_dot15d4 == None:
            self.logutil.log('Successfully tasked drone with task: {0}'.format(uuid_dot15d4))
        else:
            self.logutil.log('ERROR: Failed to Task Drone')

        # This will collect the ZigBee version:
        parameters['filter'] = {
                         'fcf': (0x0300, 0x0100), # 802.15.4 type Data
                         #TODO we can't have two byteoffset's currently in the CapturePlugin's filter handler
                         'byteoffset': (9, 0x03, 0x01) #offset within the ZB pkt for Frame Type: Command (0x0001)
                         #'byteoffset': (0x21, 0xff, 0x04) #offset within the ZB pkt for Command Identifier: Leave (0x04)
                     }
        #TODO channel needs to be set dynamically
        uuid_zbnwk = self.taskDrone(droneIndexList=[0], task_plugin='CapturePlugin',
                                    task_channel=channel, task_parameters=parameters, module_index=self.moduleIndex())
        if not uuid_zbnwk == None:
            self.logutil.log('Successfully tasked drone with task: {0}'.format(uuid_zbnwk))
        else:
            self.logutil.log('ERROR: Failed to Task Drone')

        # Get packets from database and run statistics
        while not self.shutdown_event.is_set():
            #pkts = self.getPackets(uuidFilterList=[uuid_dot15d4, uuid_zbnwk], new=True)
            pkts = self.getPackets(uuidFilterList=[uuid_zbnwk], new=True)
            self.logutil.debug("Found {0} packets since last check.".format(len(pkts)))
            for pkt in pkts:
                self.logutil.debug("Got pkt from DB: {0}".format(pkt))
                spkt = Dot15d4FCS(pkt.pbytes)

                msg         = None
                device      = None
                coordinator = None
                panid       = spkt.dest_panid

                # It may be an 802.15.4 disassociation, which our uuid_dot15d4 should collect
                if Dot15d4CmdDisassociation in spkt:
                    event_name = 'Dissassociation Frame Detected'
                    self.logutil.log("EVENT: {0}: {1}.".format(event_name, spkt.summary()))
                    if spkt.disassociation_reason == 0x02: # The device wishes to leave the PAN
                        msg         = "802.15.4 Dissassociation Frame (Reason: Device Wishes to Leave)"
                        device      = spkt.src_addr
                        coordinator = spkt.dest_addr
                    elif spkt.disassociation_reason == 0x01: # The coordinator wishes the device to leave the PAN
                        msg         = "802.15.4 Dissassociation Frame (Reason: Coordinator Wishes Device to Leave)"
                        device      = spkt.dest_addr
                        coordinator = spkt.src_addr
                    else:
                        msg         = "802.15.4 Dissassociation Frame (Reason has an unexpected value)"
                    self.registerEvent(name=event_name, details={'msg':msg}, related_packets=[pkt.id])
                # Or it's a ZigBee frame, which our uuid_zbnwk task should request
                elif ZigbeeNWKCommandPayload in spkt:
                    event_name = 'ZigbeeNWKCommandPayload Frame Detected'
                    self.logutil.log('EVENT: {0}: {1}'.format(event_name, spkt.summary()))
                    self.registerEvent(name=event_name, details={}, related_packets=[pkt.id])
                    if spkt.cmd_identifier != "leave":
                        continue    # It isn't the disassoc we're looking for
                    elif spkt.request == 0:  # Device leaving
                        msg         = "ZigBee Dissassociation Command (Reason: Device Wishes to Leave)"
                        device      = spkt.ext_src  #TODO include spkt.src_addr which is the short address
                        coordinator = spkt.ext_dst
                        if spkt.src_addr != spkt.source:
                            msg    += " (Unexpected mismatch of source short addresses)"
                        if spkt.dest_addr != 0x0 or spkt.destination != 0x0:
                            msg    += " (Unexpected non-0x0000 value for destination, expect it to target the coordinator)"
                    elif spkt.request == 1:  # Coordinator booting device
                        msg         = "ZigBee Dissassociation Command (Reason: Coordinator Wishes Device to Leave)"
                        device      = spkt.ext_dst
                        coordinator = spkt.ext_src  #TODO include spkt.src_addr which is the short address
                        if spkt.dest_addr != spkt.destination:
                            msg    += " (Unexpected mismatch of source short addresses)"
                        if spkt.src_addr != 0x0 or spkt.source != 0x0:
                            msg    += " (Unexpected non-0x0000 value for source, expect it to come from the coordinator)"
                    else:
                        msg         = "802.15.4 Dissassociation Frame (Reason has an unexpected value)"
                # Or we don't want this packet, which shouldn't happen based on our front-end selection
                else:
                    self.logutil.debug("query got us a frame we didn't want: {0}.".format(spkt.summary()))
                    continue
                
                # Now publish the event
                #TODO switch to correct call to DB
                self.logutil.log("alert: {0} / coordinator={1}, device={2}.".format(msg, coordinator, device))

            time.sleep(15)
        self.shutdown()


    def cleanup(self):
        pass











