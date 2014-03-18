#!/usr/bin/python

import os
import json
import traceback
from time import sleep
from datetime import datetime
from uuid import uuid4
from multiprocessing import Process

from beekeeperwids.wids.database import *
from beekeeperwids.wids.client import WIDSClient
from beekeeperwids.utils import KBLogUtil, dateToMicro

import signal
import sys

#TODO - import sendPOST from utils

class AnalyticModule(Process):

    def __init__(self, settings, config, shutdown_event, name):
        Process.__init__(self)
        self.name = name
        self.settings = settings
        self.config = config
        self.shutdown_event = shutdown_event
        self.database = DatabaseHandler(self.config.name)
        self.logutil = KBLogUtil(self.config.name, self.name, None)
        self.wids_api = WIDSClient(self.config.server_ip, self.config.server_port)
        self.tasks = {}
        self.active = False
        self.running = False

    def SIGTERM(self,a,b):
        self.logutil.log('SIGTERM')
        self.shutdown()

    def moduleIndex(self):
        return self.settings.get('module_index')

    def waitForWIDS(self):
        while not self.wids_api.isActive():
            sleep(0.1)

    def taskDrone(self, droneIndexList, task_plugin, task_channel, task_parameters, module_index):
        try:
            task_uuid = str((uuid4()))
            (error,data) = self.wids_api.taskDrone(droneIndexList, task_uuid, task_plugin, task_channel, task_parameters, module_index)
            if error == None:
                self.tasks[task_uuid] = {'plugin':task_plugin, 'channel':task_channel, 'parameters':task_parameters, 'drones':droneIndexList, 'uuid':task_uuid, 'module_index':module_index}
                return task_uuid 
            else:
                return False
        except Exception:
            etb = traceback.format_exc()
            self.logutil.trace(etb)
            return False

    def detaskDrone(self, droneIndexList, uuid):
        self.logutil.log('Detasking UUID: {0} from Drones: {1}'.format(uuid,droneIndexList))
        try:
            self.wids_api.detaskDrone(droneIndexList, uuid)
        except Exception:
            etb = traceback.format_exc()
            self.logutil.trace(etb)

    def detaskAll(self):
        self.logutil.log('Detasking all active tasks ({0} found)'.format(len(self.tasks.values())))
        for task in self.tasks.values():
            uuid = task.get('uuid')
            droneIndexList = task.get('drones')
            self.detaskDrone(droneIndexList, uuid)

    def getPackets(self, valueFilterList=[], uuidFilterList=[], new=False, maxcount=0, count=False):
        return self.database.getPackets(valueFilterList, uuidFilterList, new, maxcount, count)

    def getEvents(self, valueFilterList=[], new=False, maxcount=0, count=False):
        return self.database.getPackets(valueFilterList, new, maxcount, count)

    def registerEvent(self, name, details={}, related_packets=[], related_uuids=[]):
        event_data = {'module':self.name, 'name':name, 'details':details, 'related_packets':related_packets, 'related_uuids':related_uuids, 'datetime':dateToMicro(datetime.utcnow())}
        return self.database.storeEvent(event_data)

    def generateAlert(self, alert_name):
        return self.database.storeAlert(alert_name)

    def cleanup(self):
        '''
        This should be overridden by modules which need to do housekeeping 
        before shutdown.
        '''
        pass

    def shutdown(self, detask=True):
        self.logutil.log('Received Shutdown Request')
        self.cleanup()
        self.logutil.log('Module Shutdown Complete')
        sys.exit()





