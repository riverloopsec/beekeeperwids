#!/usr/bin/python

'''
This app is intended to monitor a network for specific packets. When a packet meeting a specific filter is detected,
and event alert is generated
'''

import flask, json
import os, sys
from multiprocessing import Pipe, Event, Manager
from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
#from sqlalchemy import create_engine
Base = declarative_base()

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
                #self.bytes = data['bytes']
                self.rssi = pktdata['rssi']
                self.validcrc = pktdata['validcrc']


class DatabaseHandler:
	# the database is implemeneted in SQLAlhemy to facilitate packet lookups
	# this allows complex object-level queries without dealing with SQL 
	# this class should probably be a part of the BaseApp class
	def __init__(self, database='sqlalchemy_monitor.db'):
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

class MonitorApp:
	# this class provides the management logic for the app. it manages the external server process
	# and implements the analytic & eventing modules

	def __init__(self):
		self.packetDatabase = None
		self.eventDatabase = None
		self.networkDatabase = None
		self.dbHandler = DatabaseHandler()
		self.analytic_plugins = []
		self.loadAnalyticPlugins()
		self.launchProcesses()

	def loadAnalyticPlugins()
		pass

	def launchProcesses(self):
		pass


class DataListener(Process):
	# this class is intended to run an an independent process that will receive and store packets
	# the packets are received by a flask web server and stored in an SQLAlchemy database
	def __init__(self):
		self.dbHandler = DatabaseHandler()
		self.port = 8888
		self.startServer()
	def startServer(self):
		app = flask.Flask(__name__)
		app.add_url_rule('/data', None, self.recvData, methods=['POST'])
		app.run(debug=True, port=self.port)
	def stopServer(self):
		pass
	def recvData(self):
		data = json.loads(flask.request.data)
		uuid = data['uuid']
		packet = data['pkt']
		#packet.display()
		self.dbHandler 
		self.dbHandler.storePacket(packet)
		return 'DATA RECEIVED'


class AnalyticPluginPacketCount(Process):
	# this sample plugin counts how many packets have been collected and prints it to screen

	def __init__(self, dbHandler):
		self.dbHandler = dbHandler
		self.run()

	def run(self):
		# check if new packets are present
		if len(self.dbHandler.getPackets()) > 20:
			print("Received more than 20 packets!!!")



if __name__ == '__main__':
	MonitorApp()

