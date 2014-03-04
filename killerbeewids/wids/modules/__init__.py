#!/usr/bin/python

import os
import json
import traceback
from datetime import datetime
from uuid import uuid4
from multiprocessing import Process

from killerbeewids.wids.database import *
from killerbeewids.wids.client import WIDSClient
from killerbeewids.utils import KBLogUtil, dateToMicro

#TODO - import sendPOST from utils

class AnalyticModule(Process):

    def __init__(self, settings, config, name):
        Process.__init__(self)
        self.name = name
        self.settings = settings
        self.config = config
        self.database = DatabaseHandler(self.config.name)
        self.logutil = KBLogUtil(self.config.name, self.name, None)
        self.widsclient = WIDSClient(self.config.server_ip, self.config.server_port)
        self.tasks = {}
        self.active = False
        self.running = False

    def taskDrone(self, droneIndexList, task_plugin, task_channel, task_parameters):
        try:
            task_uuid = str((uuid4()))
            json_result = self.widsclient.taskDrone(droneIndexList, task_uuid, task_plugin, task_channel, task_parameters)
            result = json.loads(json_result)
            if result.get('success'): 
                self.tasks[task_uuid] = {'plugin':task_plugin, 'channel':task_channel, 'parameters':task_parameters, 'drones':droneIndexList}
                return task_uuid 
            else:
                return False
        except Exception:
            etb = traceback.format_exc()
            self.logutil.trace(etb)
            return False

    def detaskDrone(self, droneIndexList, uuid):
        pass

    def detaskAll(self):
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

    def shutdown(self):
        self.logutil.log('Received Shutdown Request')
        self.active = False
        while self.running:
            pass
        self.detaskAll()
        self.cleanup()
        self.logutil.log('Module Shutdown Complete')
        self.terminate()



