#!/usr/bin/python

import os
import json
from uuid import uuid4
from multiprocessing import Process
from killerbeewids.wids.database import *
from killerbeewids.wids import WIDSClient
from killerbeewids.utils import KBLogUtil

# TODO - incorporate shutdown event & implement proper shutdown sequence
# TODO - implement proper evenet generation mechanism

class AnalyticModule(Process):

    def __init__(self, settings, config, name):
        Process.__init__(self)
        self.name = name
            self.settings = settings
        self.config = config
            self.tasks = {}
        self.lastPacketIndex = 0
            self.active = False
            self.running = False
        self.database = DatabaseHandler(self.config.name)
        self.logutil = KBLogUtil(self.config.name, self.config.workdir, self.name, None)
            self.widsclient = WIDSClient(self.config.server_ip, self.config.server_port)

    def taskDrone(self, droneIndexList, task_plugin, task_channel, task_parameters):
        task_uuid = str((uuid4()))
        json_result = self.widsclient.taskDrone(droneIndexList, task_uuid, task_plugin, task_channel, task_parameters)
        result = json.loads(json_result)
        success = result.get('success')
        if success:
            self.tasks[task_uuid] = {'plugin':task_plugin, 'channel':task_channel, 'parameters':task_parameters}
            return task_uuid
        else:
            return None

    def getCallbackUrl(self):
        return 'http://{0}:{1}/data/upload'.format(self.config.server_ip, self.config.server_port)

    def detaskDrone(self, uuid, plugin, channel, parameters):
        pass

    def getPackets(self, queryFilter=[], uuid=[]):
        query = self.database.session.query(Packet)
        if not len(uuid) == 0:
            query.filter(Packet.uuid.in_(uuid))
        for key,operator,value in queryFilter:
            #print(key,operator,value)
            query = query.filter('{0}{1}{2}'.format(key,operator,value))
        results = query.all()
        return results

    def getNewPackets(self, queryFilter=[], uuid=[]):
        queryFilter.append(('id','>',self.lastPacketIndex))
        results = self.getPackets(queryFilter, uuid)
        if len(results) > 0:
            self.lastPacketIndex = results[-1].id
        return results

    def getEvents(self):
        pass

        def generateEvent(self):
            pass

    def registerEvent(self):
        pass

    def detaskAll(self):
        '''
        This function will detask all the running tasks on the drone prior to shutdown
        '''
            pass

    def shutdown(self):
        self.logutil.log('\t\tReceived Shutdown Request')
        self.active = False
        while self.running:
            pass
        self.detaskAll()
        self.cleanup()
        self.logutil.log('\t\t\tModule Shutdown Complete')
        self.terminate()
