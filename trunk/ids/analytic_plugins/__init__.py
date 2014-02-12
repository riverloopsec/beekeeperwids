#!/usr/bin/python


class BaseAnalyticPlugin:

	def __init__(self, databaseHandler):
		self.name = 'someplugin'
		self.db = databaseHandler
		pass

	def run(self):
		while True:
			pass

			# get data from database

			# run some test

			# if condition is met, execute action


	def registerEvent(self, event):
		# register an event in the database
		self.db.registerEvent(self.name, event)


	def executeAction(self, eventPlugin, params):
		# check that plugin exists
		# execute action
		pass

