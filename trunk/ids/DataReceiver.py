#!/usr/bin/python

debug=True

import json.loads

class DataReceiverProcess(Process):

	def __init__(self, database, port=50888):
		self.port = port
		self.database = database
		self.run()
	def run(self):
		app = flask.Flask(__name__)
		app.add_url_rule('/data', None, self.recvData, methods=['POST'])
		app.run(debug, port=self.port)
	def stop(self):
		pass
	def recvData(self):
		data = json.loads(flask.request.data)
		uuid = data.get['uuid']
		packet = data.get['pkt']
		self.database.storePacket(packet)
		return 'DATA RECEIVED'
		
