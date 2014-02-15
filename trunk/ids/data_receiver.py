#!/usr/bin/python

debug=True

from multiprocessing import Process
import json
import flask
import sys
import signal
import time
import os

class DataReceiverProcess(Process):

	def __init__(self, database, logger, parameters):
		Process.__init__(self)
		signal.signal(signal.SIGTERM, self.SIGTERM)
		#signal.signal(signal.SIGINT, self.SIGINT)
		self.parameters = parameters
		self.database = database
		self.active = True

	def SIGINT(self, sig, frame):
		print("DataReciever: SIGINT")

	def SIGTERM(self, sig, frame):
		print("DataReciver: SIGTERM")
		sys.exit()

	def run(self):
		
		time.sleep(2)
		print("DataReceiver: {0}".format(os.getpid()))

		if True:
			app = flask.Flask(__name__)
			app.add_url_rule('/data', None, self.recvData, methods=['POST'])
			app.run(debug=False, port=self.parameters.get('port'))


	def stop(self):
		sys.exit()
	def recvData(self):
		print("received packet!!!!")
		data = json.loads(flask.request.data)
		print(data.get('uuid'))
		#print(data)
		#uuid = data.get['uuid']
		#packet = data.get['pkt']
		#self.database.storePacket(packet)
		return 'DATA RECEIVED'
		

#DataReceiverProcess(None, None, {'port':8888})
