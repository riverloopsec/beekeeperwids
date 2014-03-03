#!/usr/bin/python

import os
import json
import traceback
from uuid import uuid4
from multiprocessing import Process
from killerbeewids.wids.database import *
from killerbeewids.wids.client import WIDSClient
from killerbeewids.utils import KBLogUtil

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


    def getPackets(self, valueFilterList=[], uuidFilterList=[], new=False, maxcount=0, count=False):
        return self.database.getPackets(valueFilterList, uuidFilterList, new, maxcount, count)

    '''
    this code is being moved directly to DatabaseHandler


    def getPackets(self, queryFilter=[], uuid=[], count=False):
        query = self.database.session.query(Packet)
        if len(uuid) > 0:
            query.filter(Packet.uuid.in_(uuid))
        for key,operator,value in queryFilter:
            #print(key,operator,value)
            query = query.filter('{0}{1}{2}'.format(key,operator,value))
        if count:
            return query.count()
        else:
            return query.all()

    def getNewPackets(self, queryFilter=[], uuid=[]):
        #TODO there is an issue where 2 different getNewPackets calls in the
        #     same module will set different lastPacketIndex values and thus
        #     may miss or duplicate packets!
        queryFilter.append(('id','>',self.lastPacketIndex))
        results = self.getPackets(queryFilter, uuid)
        #TODO need to make sure we're indexing to the highest id, as 
        #     are we sure the DB will always return (in this function) with the
        #     highest ID last?
        if len(results) > 0:
            self.lastPacketIndex = results[-1].id
        return results

    def getPackets(self, filters=[], new=False):
        return self.database.getPackets(filters, new)
    '''


    def detaskAll(self):
        for task in self.tasks.values():
            uuid = task.get('uuid')
            droneIndexList = task.get('drones')
            self.detaskDrone(droneIndexList, uuid)
    
    def getEvents(self, filters=[], new=False):
        return self.database.getEvents(filters, new)

    def generateEvent(self, event_data):
        return self.database.storeEvent(event_data)

    def shutdown(self):
        self.logutil.log('\t\tReceived Shutdown Request')
        self.active = False
        while self.running:
            pass
        self.detaskAll()
        self.cleanup()
        self.logutil.log('\t\t\tModule Shutdown Complete')
        self.terminate()



