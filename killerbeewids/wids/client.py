#!/usr/bin/python

import logging
import flask
import json
import os
import sys
import signal
import time
import urllib2, urllib
import traceback
from collections import OrderedDict
from xml.etree import ElementTree as ET
from multiprocessing import Pipe, Event, Manager, Lock

'''
from killerbeewids.utils import KBLogUtil
from killerbeewids.drone import DroneClient
from killerbeewids.wids.database import DatabaseHandler
from killerbeewids.wids.engine import WIDSRuleEngine
from killerbeewids.wids.modules.beaconreqscan import BeaconRequestMonitor
'''

class WIDSClient:

    def __init__(self, address, port):
        self.address = address
        self.port = port

    def getStatus(self):
        resource = '/status'
        return self.sendPOST(self.address, self.port, resource, {})

    def addDrone(self, drone_url):
        resource = '/drone/add'
        parameters = {'url':drone_url}
        return self.sendPOST(self.address, self.port, resource, parameters)

    def delDrone(self, drone_index):
        resource = '/drone/delete'
        parameters = {'drone_index':drone_index}
        return self.sendPOST(self.address, self.port, resource, parameters)

    def taskDrone(self, droneIndexList, task_uuid, task_plugin, task_channel, task_parameters):
        resource = '/drone/task'
        parameters = {'droneIndexList':droneIndexList, 'uuid':task_uuid, 'channel':task_channel, 'plugin':task_plugin, 'parameters':task_parameters}
        return self.sendPOST(self.address, self.port, resource, parameters)

    def loadModule(self, name, settings):
        resource = '/module/load'
        parameters = {'name':name, 'settings':settings}
        return self.sendPOST(self.address, self.port, resource, parameters)

    def unloadModule(self, module_index):
        resource = '/module/unload'
        parameters = {'module_index':module_index}
        return self.sendPOST(self.address, self.port, resource, parameters)


    def sendGET(self, address, port, resource):
        pass

    def sendPOST(self, address, port, resource, data):
        url = "http://{0}:{1}{2}".format(address, port, resource)
        http_headers = {'Content-Type' : 'application/json', 'User-Agent' : 'DroneClient'}
        post_data_json = json.dumps(data)
        request_object = urllib2.Request(url, post_data_json, http_headers)
        try:
            response_object = urllib2.urlopen(request_object)
        except:
            print('failed to connect to drone')
            return json.dumps({'success':False, 'data':'Error - could not connect to drone'})

        try:
            response_string = response_object.read()
            return json.dumps({'success':True, 'data':response_string})
        except:
            return json.dumps({'success':False, 'data':'Error - failed to read response from drone'})


