#!/usr/bin/python

import sys
import json
import flask
import sys
import signal
import time
import os
from multiprocessing import Process
from killerbeewids.trunk.wids.database import DatabaseHandler
from killerbeewids.trunk.utils import KBLogger

class WIDSWebServer(Process):

	def __init__(self, config):
		Process.__init__(self)
		signal.signal(signal.SIGTERM, self.SIGTERM)
		self.config = config
		self.logger = KBLogger(config.settings.get('logfile'))
		#self.database = DatabaseHandler(config.settings.get('database'))
	def SIGTERM(self, sig, frame):
		#self.logger.entry("WIDSWebServer", "SIGTERM")
		sys.exit()
	def run(self):
		self.logger.entry("WIDSWebServer", "Starting Execution")
		app = flask.Flask(__name__)
		app.add_url_rule('/data', None, self.recvData, methods=['POST'])
		app.run(debug=False, port=int(self.config.settings.get('server_port')))
	def recvData(self):
		#self.logger.entry("WIDSWebServer", "Received Request", "DEBUG")
		data = json.loads(flask.request.data)
		print(data.get('uuid'))
		#print(data)
		#uuid = data.get['uuid']
		#packet = data.get['pkt']
		#self.database.storePacket(packet)
		return 'DATA RECEIVED'
		

