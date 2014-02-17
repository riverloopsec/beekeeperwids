#!/usr/bin/python

import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
Base = declarative_base()

'''
class Drone(Base):
	__tablename__ = 'drone'
'''


class Message(Base):
	__tablename__ = 'message'
	id = Column(Integer, primary_key=True)

	def __init__(self, msgdata):
		self.src = msgdata.get('src')
		self.dst = msgdata.get('dst')
		self.code = msgdata.get('code')
		self.parameters = msgdata.get('parameters')


class Packet(Base):
	__tablename__ = 'packet'
	id = Column(Integer, primary_key=True)
	source = Column(String(250))
	datetime = Column(String(250))
	dbm = Column(String(250))
	rssi = Column(String(250))
	validcrc = Column(String(250))

	def __init__(self, pktdata):
		print(pktdata)
		self.source = pktdata.get('location')
		self.datetime = pktdata.get('datetime')
                self.dbm = pktdata['dbm']
                self.bytes = data['bytes']
                self.rssi = pktdata['rssi']
                self.validcrc = pktdata['validcrc']
		self.size = len(self.bytes)
		

class DatabaseHandler:
	# the database is implemeneted in SQLAlhemy to facilitate packet lookups
	# this allows complex object-level queries without dealing with SQL 
	# this class should probably be a part of the BaseApp class
	def __init__(self, database):
		print("Initializing DatabaseHandler")
		self.engine = create_engine("sqlite:///{0}".format(database), echo=True)
		if not os.path.isfile(database):
			self.createDB()
		self.session = sessionmaker(bind=self.engine)()
	def createDB(self):
		Base.metadata.create_all(self.engine)

	def storePacket(self, pktdata):
		self.session.add(Packet(pktdata))
		self.session.commit()

	def getPackets(self, pktfilter=None, maxcount=None):
		results = self.session.query(Packet).all()
		return results

	def checkNewPackets(self):
		return True


	def storeMessage(self, msgdata):
		self.session.add(Message(msgdata))
		self.session.commit()

	def getMessages(self, msgfilter=None):
		results = self.session.query(Message).all()
		return results

	
	def checkNewMessages(self):
		return True









