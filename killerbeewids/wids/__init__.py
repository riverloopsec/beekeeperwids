#!/usr/bin/python

from killerbeewids.drone.client import DroneClient

class ModuleContainer:
    def __init__(self, index, name, settings, process, shutdown_event):
        self.index = index
        self.name = name
        self.settings = settings
        self.process = process
        self.shutdown_event = shutdown_event
    def json(self):
        return {'index':self.index, 'name':self.name, 'settings':self.settings, 'process':self.process.pid}


class DroneContainer:
    def __init__(self, index, address, port):
        self.index = index
        self.address = address
        self.port = port
        self.tasks = {}
        self.plugins = {}
        self.id = None
        self.status = None
        self.heartbeat = None
        self.api = DroneClient(self.address, self.port)
    def release(self):
        #TODO - implement drone release
        pass
    def json(self):
        return {'index':self.index, 'url':self.url, 'tasks':self.tasks, 'plugins':self.plugins, 'status':self.status, 'heartbeat':self.heartbeat}


class RuleContainer:
    def __init__(self, index, rid, name, conditions, actions):
        self.index = index
        self.rid = rid
        self.name = name
        self.event_index = 0
        self.conditions = conditions
        self.actions = actions
        self.read = False
        self.history = []
    def json(self):
        return {'id':self.id, 'conditions':self.conditions, 'action':self.actions}


class TaskContainer:
    def __init__(self, id, uuid, plugin, channel, parameters, drones, module_index):
        self.id = id
        self.uuid = uuid
        self.plugin = plugin
        self.channel = channel
        self.parameters = parameters
        self.drones = drones
        self.module_index = module_index
    def json(self):
        return {'id':self.id, 'uuid':self.uuid, 'plugin':self.plugin, 'channel':self.channel, 'parameters':self.parameters}


class Configuration:
    
    def __init__(self, parameters=None, config=None):
        self.name = 'wids0'
        self.daemon_pid = None
        self.engine_pid = None
        self.server_port = 8888
        self.server_ip = '127.0.0.1'
        self.upload_url = 'http://{0}:{1}/data/upload'.format(self.server_ip, self.server_port)
        self.drones = [{'id':'drone11', 'address':'127.0.0.1', 'port':9999}]
        #self.modules = [{'name':'BeaconRequestMonitor', 'settings':{'channel':15}}]
        self.modules = [{'name':'DisassociationStormMonitor', 'settings':{'channel':15}}]

    def loadConfig(self, config):
        #TODO load all parameters above from the config file, and call this at startup
        pass

    def json(self):
        return {'name':self.name, 'daemon_pid':self.daemon_pid, 'engine_pid':self.engine_pid, 'server_port':self.server_port}

