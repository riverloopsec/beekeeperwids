#!/usr/bin/python

import os
import sys
import base64
from killerbeewids.utils import KBDIR
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, PickleType, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
Base = declarative_base()

'''
class Event(Base):
	__tablename__ = 'event'
'''




class Packet(Base):
	__tablename__ = 'packet'
	id = Column(Integer, primary_key=True)
	source = Column(String(250))
	datetime = Column(Integer())
	dbm = Column(Integer)
	rssi = Column(Integer())
	validcrc = Column(String(250))
	uuid = Column(String(250))
	bytes = Column(String(150))

	def __init__(self, pktdata):

		print(pktdata)

		self.datetime = int(pktdata.get('datetime'))
		self.source = str(pktdata.get('location'))
                self.dbm = str(pktdata['dbm'])
                self.rssi = int(pktdata['rssi'])
		self.uuid = str(pktdata['uuid'])
                #self.validcrc = str(pktdata['validcrc'])
                self.bytes = str(base64.base64decode(data['bytes']))

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









