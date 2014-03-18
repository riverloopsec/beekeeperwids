#!/usr/bin/python

import urllib2
import json
import traceback

from beekeeperwids.utils.errors import ErrorCodes as ec
from beekeeperwids.utils.rest import makeRequest

class DroneClient:

    def __init__(self, address, port):
        self.address = address
        self.port = port

    def status(self):
        resource = '/status'
        data = {}
        return makeRequest(self.address, self.port, resource, data)

    def task(self, plugin, channel, uuid, parameters):
        resource = '/task'
        data = {'plugin':plugin, 'channel':channel, 'uuid':uuid, 'parameters':parameters}
        return makeRequest(self.address, self.port, resource, data)

    def detask(self, uuid):
        resource = '/detask'
        parameters = {'uuid':uuid}
        return makeRequest(self.address, self.port, resource, parameters)


