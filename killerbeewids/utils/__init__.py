import os
import time
import datetime
import traceback
import tempfile
from xml.etree import ElementTree as ET

from killerbee import KillerBee

KB_CONFIG_PATH = os.getenv('KBWIDS_CONFIG_PATH', '/opt/kbwids/')

def dateToMicro(datetimeObject):
    delta = datetimeObject - datetime.datetime(1970,1,1)
    micro = (delta.microseconds + ((delta.seconds + delta.days * 24 * 3600) * 10**6))
    return micro

def microToDate(microseconds):
    date = datetime.datetime(1970,1,1) + datetime.timedelta(microseconds=microseconds)
    return date.strftime('%Y-%m-%d %H:%M:%S.%f')


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
    def __init__(self, app_name, process_name=None, a=None, b=None, c=None): # i <3 hakiness
        self.app_name = app_name
        self.process_name = process_name
        self.path = os.getenv('KBWIDS_LOG_PATH', tempfile.gettempdir())
        self.logfilename = '{0}/{1}.log'.format(self.path, self.app_name)
        self.pidfilename = '{0}/{1}.pid'.format(self.path, self.app_name)
        self.logfile = open(self.logfilename, 'a')

    def writePID(self):
        open(self.pidfilename, 'w').write(str(os.getpid()))

    def deletePID(self):
        os.remove(self.pidfilename)

    def getPID(self):
        return open(self.pidfilename, 'r').read()

    def startlog(self):
        self.logfile.write('='*70 + 'START' + '='*70 + '\n')

    def endlog(self):
        self.logfile.write('='*71 + 'END' + '='*71 + '\n')

    def record(self, category, msg):
        self.logfile.write(str(time.strftime('%Y-%m-%d %H:%M:%S')).ljust(21) + str(self.process_name).ljust(26) + ' : ' + str(category).ljust(8) + str(msg) + '\n')
        self.logfile.flush()

    def trace(self, etb):
        self.error('Encountered Unknown Exception, see traceback:')
        self.logfile.write('\n{0}\n'.format(etb))
        self.logfile.flush()

    def error(self, msg):
        self.record('ERROR', msg)

    def log(self, msg):
        self.record('INFO', msg)

    def debug(self, msg):
        self.record('DEBUG', msg)

    def dev(self, msg):
        self.record('DEV-DBG', msg)
        
    def cleanup(self):
        self.endlog()
        self.logfile.close()
        os.remove(self.pidfilename)

