#!/usr/bin/python

import os
import time
from killerbee import KillerBee


def getPlugin(path):
	module = '.'.join(path.split('.')[:-1])
	plugin = path.split('.')[-1]
	try:
		p = getattr(__import__(str(module), fromlist=[str(plugin)]), str(plugin))
	except(ImportError, AttributeError):
		p = None
	return p

class KBInterface(KillerBee):
        def __init__(self, device, datasource=None, gps=None):
                KillerBee.__init__(self, device, datasource, gps)
		self.device = device
                self.plugin = None
		self.active = False
	def info(self):
		if self.plugin == None:
			p = None
		else:
			p = self.plugin.info()
		return {'plugin':p, 'active':str(self.active), 'device':self.device}


class KBLogUtil:
	def __init__(self, name, path='/home/dev/etc/kb', space=24):
		self.name = name
		self.path = path
		self.space = space
		self.logfilename = '{0}/{1}.log'.format(self.path, self.name)
		self.runfilename = '{0}/{1}.run'.format(self.path, self.name)
		self.pidfilename = '{0}/{1}.pid'.format(self.path, self.name)
		self.logfile = open(self.logfilename, 'a')
	def setRun(self):
		open(self.runfilename, 'w').write('1')	
	def unsetRun(self):
		open(self.runfilename, 'w').write('0')	
	def getRunState(self):
		state = open(self.runfilename, 'r').read()
		if state == '1': return True
		else: return False
	def checkRunFile(self):
		if os.path.isfile(self.runfilename): return True
	def writePID(self):
		open(self.pidfilename, 'w').write(os.getpid())
	def getPID(self):
		return open(self.pidfilename, 'r').read()
	def logline(self):
		self.logfile.write('-'*130 + '\n')
	def endlog(self):
		self.logfile.write('====ENDLOG====\n')
		self.logfile.close()
	def log(self, process, msg, pid=0, category='INFO'):
                date = time.strftime("%Y-%m-%d %H:%M:%S")
		s = str(date).ljust(21) + str(category).ljust(6) + str(pid).ljust(7) + str(process).ljust(self.space) + ' : ' + str(msg)
                self.logfile.write(s + '\n')
                self.logfile.flush()
	def cleanup(self):
		os.remove(self.runfilename)
		os.remove(self.pidfilename)













