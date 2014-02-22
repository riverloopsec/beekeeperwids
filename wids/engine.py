#!/usr/bin/python

import time
from multiprocessing import Process

class WIDSRuleEngine(Process):

	def __init__(self, config):
		Process.__init__(self)
		self.config = config


	def run(self):
		while True:
			time.sleep(5)
			#print('[DEBUG] RuleEngine running')


