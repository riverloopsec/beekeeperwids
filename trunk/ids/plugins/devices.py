#!/usr/bin/python




def generateUUID():

	return 123456


class DetectNewDevicesPlugin:
	'''
	description: this plugins monitors the network for new devices
	author: RiverloopSecurity,LLC
	'''
	def __init__(self, widsAPI):
		self.widsAPI = widsAPI
		self.threshold = 50000
		self.run()

	def run(self):

		print("running BandwdithMonitorPlugin!")
		return

		self.byte_count = 0

		# request data
		uuid = generateUUID()
		parameters = {'channel':11, 'uuid':uuid}
		self.widsAPI.requestTask('capture', parameters)
		
		# monitor for new data
		search_parameters = {'tags':['new'], 'uuid':uuid}
		for packet in self.widsAPI.database.getPackets(search_parameters):
			byte_count += packet.byte_size
			if self.checkByteCount():
				return

	def checkByteCount(self):
		if self.byte_count > self.threshold:
			print("Met Threshold!!!!!!!!!!!!!!!!!!!!!")
			self.widsAPI.registerEvent('met bandwidth threshold')					
