#!/usr/bin/python

import sys
import json
import flask
import sys
import signal
import time
import os
from multiprocessing import Process
from killerbeewids.wids.database import DatabaseHandler
from killerbeewids.utils import KBLogUtil

class WIDSWebServer(Process):

	def __init__(self, config):
		Process.__init__(self)
		self.desc = 'Server'
		self.config = config
		self.logutil = KBLogUtil(self.config.settings.get('appname'))
		self.database = DatabaseHandler(config.settings.get('database'))

	def run(self):
		self.logutil.log(self.desc, 'Starting Execution', self.pid)
		app = flask.Flask(__name__)
		app.add_url_rule('/data', None, self.recvData, methods=['POST'])
		app.run(debug=False, port=int(self.config.settings.get('server_port')))

	def recvData(self):
		self.logutil.log(self.desc, 'Received Data', self.pid, 'DEBUG')
		data = json.loads(flask.request.data)
		packetdata = data.get('pkt')
		self.database.storePacket(packetdata)
		return 'DATA RECEIVED'
		

