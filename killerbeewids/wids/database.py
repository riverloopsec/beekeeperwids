#!/usr/bin/python

import os
import sys
from killerbeewids.utils import KBDIR
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, PickleType, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
Base = declarative_base()

'''
class Event(Base):
	__tablename__ = 'event'
'''


class TaskRequest(Base):
	__tablename__ = 'taskrequest'
	id = Column(Integer, primary_key=True)
	channel = Column(Integer)
	plugin = Column(String(100))
	parameters = Column(PickleType)
	uuid = Column(String(100))
	complete = Column(Boolean)
	def __init__(self, uuid, plugin, channel, parameters):
		self.plugin = plugin
		self.channel = channel
		self.parameters = parameters
		self.uuid = uuid
		self.complete = False


class Message(Base):
	__tablename__ = 'message'
	id = Column(Integer, primary_key=True)
	messageid = Column(Integer)
	src = Column(String(250))
	dst = Column(String(250))
	code = Column(String(250))
	request_data = Column(PickleType)
	response_data = Column(PickleType)
	resolved = Column(Boolean())
	
	def __init__(self, messageid, src, dst, code, request_data):
		self.messageid = messageid
		self.src = src
		self.dst = dst
		self.code = code
		self.request_data = request_data
		self.response_data = None
		self.resolved = False


class Packet(Base):
	__tablename__ = 'packet'
	id = Column(Integer, primary_key=True)
	source = Column(String(250))
	datetime = Column(Integer())
	dbm = Column(Integer)
	rssi = Column(Integer())
	validcrc = Column(String(250))
	uuids = Column(PickleType)

	def __init__(self, pktdata):
		self.datetime = int(pktdata.get('datetime'))
		self.source = str(pktdata.get('location'))
                self.dbm = str(pktdata['dbm'])
                #self.bytes = str(data['bytes'])
                self.rssi = int(pktdata['rssi'])
                #self.validcrc = str(pktdata['validcrc'])
		self.uuids = pktdata['uuids']

	def display(self):
		print(self.id, self.datetime, self.source, self.dbm, self.rssi)
		
# TODO - implement filters for packet queries


'''
http://docs.sqlalchemy.org/en/rel_0_9/orm/tutorial.html
'''


class DatabaseHandler:
	def __init__(self, database, path=KBDIR):
		self.engine = create_engine("sqlite:///{0}/{1}.db".format(path, database), echo=False)
		if not os.path.isfile(database):
			self.createDB()
		self.session = sessionmaker(bind=self.engine)()
	
	def createDB(self):
		Base.metadata.create_all(self.engine)

	def storePacket(self, pktdata):
		try:
			self.session.add(Packet(pktdata))
			self.session.commit()
		except Exception as e:
			print(e)

	def getPackets(self, pktfilter=None, maxcount=None):
		results = self.session.query(Packet).all()
		return results

	def checkNewPackets(self):
		return True

	def storeMessage(self, messageid, src, dst, code, request_data):
		self.session.add(Message(messageid, src, dst, code, request_data))
		self.session.commit()

	def getMessages(self, msgfilter=None):
		results = self.session.query(Message).all()
		return results

	def storeTaskRequest(self, uuid_str, plugin_str, channel_int, parameters_dict):
		tr = TaskRequest(uuid_str, plugin_str, channel_int, parameters_dict)
		self.session.add(tr)
		self.session.commit()

	def getTaskRequests(self):
		results = self.session.query(TaskRequest).all()
		return results

	def checkNewMessages(self):
		return True

	def store(self, element):
		self.session.add(element)
		self.session.commit()









