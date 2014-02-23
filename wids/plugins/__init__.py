#!/usr/bin/python

<<<<<<< HEAD
from killerbeewids.wids.database import *
=======
from multiprocessing import Process

import killerbeewids.wids.database as db
from killerbeewids.utils import KBLogUtil

# TODO - incorporate shutdown event & implement proper shutdown sequence
# TODO - implement proper evenet generation mechanism
>>>>>>> eeebcc76aeed763f83c2dd896119d7653b7dcfac

class AnalyticPlugin(Process):

        def __init__(self, config, name):
                Process.__init__(self)
                self.name = name
                self.config = config
                self.desc = None
                self.logutil = KBLogUtil(self.config.settings.get('appname'))
                self.database = db.DatabaseHandler(self.config.settings.get('database'))
		self.tasks = []
                self.PACKETS_ALL = {}
                self.lastPacket = 0


        def taskDrone(self, uuid, plugin, channel, parameters):
                self.database.storeTaskRequest(uuid, plugin, channel, parameters)

        def detaskDrone(self, uuid, plugin, channel, parameters):
                pass

        def getPackets(self, queryFilter=[]):
		query = db.session.query(Packet)
		for key,operator,value in queryFilter:
			#print(key,operator,value)
			query = query.filter('{0}{1}{2}'.format(key,operator,value))
		results = query.all()
		return results

        def getNewPackets(self, queryFilter=[]):
		queryFilter.append(('id','>',self.lastPacket))
		results = self.getPackets(queryFilter)
		self.lastPacket = results[-1].id
		return results

        def getEvents(self):
                pass


	def generateEvent(self0:
		pass

        def registerEvent(self):
                pass

        def terminate(self):
                self.detaskAll()
                self.cleanup()
                '''
                this method can be call externally to terminate the module
                '''

        def run(self):
                '''
                overwrite this method
                '''
                pass

        def detaskAll(self):
                '''
                this function will detask all the running tasks on the drone prior to shutdown
                '''

        def shutdown(self):
                '''
                overwrite this methods
                '''
                pass


