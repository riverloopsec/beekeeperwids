#!/usr/bin/python

import os
import time
import datetime
import traceback
from xml.etree import ElementTree as ET

from killerbee import KillerBee

def dateToMicro(datetimeObject):
    delta = datetimeObject - datetime.datetime(1970,1,1)
    micro = (delta.microseconds + ((delta.seconds + delta.days * 24 * 3600) * 10**6))
    return micro

def microToDate(microseconds):
    date = datetime.datetime(1970,1,1) + datetime.timedelta(microseconds=microseconds)
    return date.strftime('%Y-%m-%d %H:%M:%S.%f')

def getDronePluginLibrary():
    library = {}
    filepath = '{0}/drone/plugins/pluginlibrary.xml'.format(KBPATH)
    root = ET.parse(filepath).getroot()
    for plugin in root.findall('plugin'):
        name = plugin.get('name')
        modulepath = plugin.get('modulepath')
        library[name] = modulepath
    return library

def loadModuleClass(name):
    # step 1 - load library of available modules
    library = {}
    filepath = '{0}/wids/modules/modules.xml'.format(KBPATH)
    root = ET.parse(filepath).getroot()
    for plugin in root.findall('module'):
        name = plugin.get('name')
        path = plugin.get('path')
        library[name] = path

    #print("///////// loadModuleClass /////////")
    #print('library: {0}'.format(library))
    #print('name: {0}'.format(name))
    #print('/////////////////////////////////////')

    # step 2 - check if requested module is in library, if not return None
    if not name in library.keys():
        return None

    # step 3 - load library class
    path = library[name]
    try:
        p = getattr(__import__(str(path), fromlist=[str(name)]), str(name))
    except(ImportError, AttributeError, ValueError) as e:
        print(e)
        p = None
    return p

'''
def loadPluginClass(name):
    # step 1 - load library of available modules
    library = {}
    filepath = '{0}/drone/plugins/plugins.xml'.format(KBPATH)
    root = ET.parse(filepath).getroot()
    for plugin in root.findall('plugin'):
        name = plugin.get('name')
        path = plugin.get('path')
        library[name] = path
    # step 2 - check if requested module is in library, if not return None
    if not name in library.keys():
        return None
    # step 3 - load library class
    path = library[name]
    try:
        p = getattr(__import__(str(path), fromlist=[str(name)]), str(name))
    except(ImportError, AttributeError, ValueError) as e:
        print(e)
        p = None
    return p
'''


def checkDronePlugin(name):
    '''
    checks if the plugin exists
    '''
    # step 1 - check if the plugin is listed in the plugin list
    library = getDronePluginLibrary()
    if name in library.keys():
        module = library[name]
    elif name in library.values():
        module = name
    else:
        module = name

    # check if plugin can be loaded
    plugin = getPlugin(module)
    if not plugin == None:
        return module
    else:
        return None


def getPlugin(name):

    library = getDronePluginLibrary()
    if name in library.keys():
        path = library[name]
    elif name in library.values():
        path = name
    else:
        path = name

    module = '.'.join(path.split('.')[:-1])
    plugin = path.split('.')[-1]
    try:
        p = getattr(__import__(str(module), fromlist=[str(plugin)]), str(plugin))
    except(ImportError, AttributeError, ValueError) as e:
        print(e)
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
    def __init__(self, name, process_name=None, process_pid=None, space=24):
        self.name = name
        self.path = os.environ.get('KBWIDS_LOG_PATH')
        self.process_name = process_name
        self.process_pid = process_pid
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
        open(self.pidfilename, 'w').write(str(os.getpid()))
    def deletePID(self):
        os.remove(self.pidfilename)
    def getPID(self):
        return open(self.pidfilename, 'r').read()
    def logline(self):
        self.logfile.write('-'*130 + '\n')
    def endlog(self):
        self.logfile.write('====ENDLOG====\n')
        self.logfile.close()
    def trace(self, etb):
        self.logfile.write('\n{0}\n'.format(etb))
        self.logfile.flush()
    def log(self, msg, category='INFO'):
        date = time.strftime('%Y-%m-%d %H:%M:%S')
        s = str(date).ljust(21) + str(category).ljust(6) + str(self.process_pid).ljust(7) + str(self.process_name).ljust(self.space) + ' : ' + str(msg)
        self.logfile.write(s + '\n')
        self.logfile.flush()
    def cleanup(self):
        os.remove(self.runfilename)
        os.remove(self.pidfilename)



if __name__ == '__main__':
    pass
    #print(checkDronePlugin('CapturePlugin'))
