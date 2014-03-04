#!/usr/bin/python

import json
import os
import sys
import time
import traceback
import urllib2

class WIDSClient:

    def __init__(self, address, port):
        self.address = address
        self.port = port

    def getAlerts(self):
        resource = '/alert'
        return self.sendPOST(self.address, self.port, resource, {})

    def generateAlert(self, alert_name):
        resource = '/alert/generate'
        return self.sendPOST(self.address, self.port, resource, {'alert_name':alert_name})

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


