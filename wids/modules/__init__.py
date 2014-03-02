#!/usr/bin/python

from uuid import uuid4
import os
from killerbeewids.wids.database import *
from multiprocessing import Process

import killerbeewids.wids.database as db
from killerbeewids.utils import KBLogUtil

# TODO - incorporate shutdown event & implement proper shutdown sequence
# TODO - implement proper evenet generation mechanism

class AnalyticModule(Process):

        def __init__(self, parameters, config, name):
                Process.__init__(self)
                self.name = name
		self.parameters = parameters
                self.config = config
		self.logutil = None
		self.db = None

		self.tasks = {}
                self.lastPacket = 0
		self.active = True


	def configure(self):
		print('configuring module')
                self.database = db.DatabaseHandler(self.config.name)
                self.logutil = KBLogUtil(self.config.name, self.config.workdir, self.name, os.getpid())


        def taskDrone(self, plugin, channel, parameters):
		uuid = (uuid4())
                mID = self.database.storeTaskRequest(uuid, plugin, channel, parameters)

		# figure out how to wait until messages is resolve

		if result:
			self.tasks[uuid] = {'plugin':plugin, 'channel':channel, 'parameters':parameters}
			return uuid
		else:
			return None


        def detaskDrone(self, uuid, plugin, channel, parameters):
		#mID = self.database.storeMessagre(....)
                pass


        def getPackets(self, queryFilter=[], uuid=[]):
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


	def generateEvent(self):
		pass

        def registerEvent(self):
                pass



        def detaskAll(self):
                '''
                this function will detask all the running tasks on the drone prior to shutdown
                '''

        def shutdown(self):
		self.logutil.log('Received Shutdown Request')
		# set active flag to False, and wait for main executing to stop running
		self.active = False
		while self.running:
			pass
		# send signal to drone to remove all tasking
                self.detaskAll()
		# execute cleanup procedures
                self.cleanup()
		self.logutil.log('\tModule Shutdown Complete')


