#!/usr/bin/python

import traceback
import urllib2
import json
from killerbeewids.utils.errors import ErrorCodes as ec

def makeRequest(address, port, resource, data=None):
    url = "http://{0}:{1}{2}".format(address, port, resource)
    http_headers = {'Content-Type' : 'application/json', 'User-Agent' : 'DroneClient'}

    if data == None:
        request_object = urllib2.Request(url, None, http_headers)
    else:
        request_object = urllib2.Request(url, json.dumps(data), http_headers)

    try:
        response_object = urllib2.urlopen(request_object)
        response_data = json.loads(response_object.read())
        error = response_data.get('error')
        data  = response_data.get('data')
        return (error, data)
    except urllib2.URLError as e:
        if str(e) == '<urlopen error [Errno 111] Connection refused>':
            error = ec.ERROR_DRONE_ConnectionRefused
            data = None
        else:
            error = ec.ERROR_GENERAL_UnknownUrllib2Error
            data = traceback.format_exc()
        return (error,data)
    except Exception:
        error = ec.ERROR_GENERAL_UnknownException
        etb = traceback.format_exc()
        return (error,etb)

