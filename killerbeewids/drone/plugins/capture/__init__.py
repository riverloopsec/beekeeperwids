# Plugin for drone to preform raw PCAP capture, with optional filters applied.

import cPickle
import time, os
from multiprocessing import Pipe, Event, Manager

from cap_filter_process import FilterProcess
from cap_sniffer_process import SnifferProcess

from killerbeewids.drone.plugins import BaseDronePlugin


class CapturePlugin(BaseDronePlugin):
	def __init__(self, interfaces, channel, drone):
		BaseDronePlugin.__init__(self, interfaces, channel, drone)
		self.desc = 'CapturePlugin.{0}'.format(channel)
		
		self.logutil.log('Initializing')

		# Select interface
		try:
			self.kb = self.interfaces[0]
			self.kb.set_channel(self.channel)
			self.kb.active = True
		except Exception as e:
			print("failed to use interface")
			self.status = False
		# Pipe from the tasker to the filter module, used to send pickled tasking dictionaries (simple DictManager)
		recv_pconn, recv_cconn = Pipe()
		task_pconn, self.task_cconn = Pipe()
		# Start the filter up
		self.p_filt = FilterProcess(recv_pconn, task_pconn, self.done_event, self.task_update_event, drone, self.desc)
		self.p_filt.start()
		self.logutil.log('Launched FilterProcess ({0})'.format(self.p_filt.pid))
		self.childprocesses.append(self.p_filt)
		# Start the receiver up
		self.p_recv = SnifferProcess(recv_cconn, self.kb, self.done_event, self.drone, self.desc)
		self.p_recv.start()
		self.logutil.log('Launched SnifferProcess: ({0})'.format(self.p_recv.pid))
		self.childprocesses.append(self.p_recv)

	def task(self, uuid, data):
		self.logutil.log('Adding Task: {0}'.format(uuid))
		if uuid in self.tasks:
			return False
		self.tasks[uuid] = data
		self.__update_filter_tasking()
		return True

	def detask(self, uuid):
		res = None	
		if uuid in self.tasks:	
			res = self.tasks.get(uuid)	
			del self.tasks[uuid]	
		else:	
			return False	
		if len(self.tasks) == 0:	
			# Time to shut the whole party down, as we don't have any more tasks	
			self.logutil.log('No remaining tasks, shutting down plugin')
			self.shutdown()	
			#TODO return something to indicate a total shutdown also	
		else:	
			# We made a change to tasking, let's implement it	
			self.__update_filter_tasking()	
		return res	

	def __update_filter_tasking(self):
		#print("Tasking added:", cPickle.dumps(self.tasks).encode('hex'))
		self.logutil.log('New Tasking Added')
		self.task_cconn.send(cPickle.dumps(self.tasks))
		self.task_update_event.set()

'''
class CapturePluginOld(object):
    def __init__(self, kblist, data):
        ''
        ae are given a list of KillerBee() class objects for the interfaces
        we can use (in this case capture on), and a data object of other
        data we may need (in this case the channel number).
        Check the status flag that this sets to see if initialization 
        was successful in the calling function.
        ''
        # Managers are a pain, so CapturePlugin keeps the master dictionary
        # of tasking relavent to it, and sends updates of tasking to the
        # FilterProcess which actually uses it whenever it gets an update.
        self.tasks  = dict() #dictionary is UUID: data				
        
		self.status = True
        if len(kblist) != 1 or 'channel' not in data:
            self.status = False
        else:
            channel = data.get('channel')
            self.kb = kblist[0]
            try:
                self.kb.set_channel(channel)
            except Exception as e:
                #TODO tune exceptions and cleanup instance/device as needed
                print("KillerBee instantiation failure: ({0}).".format(e))
                self.status = False
		

        if self.status:
            print("KillerBee instance to use for CapturePlugin ch {0} is {1}".format(channel, self.kb))

            # Pipe from the sniffer (receiver) to the filter module
            recv_pconn, recv_cconn = Pipe()
            # Create an event to signal when we want to shut down
            self.done_event = Event()

            # Pipe from the tasker to the filter module, used to send pickled tasking dictionaries (simple DictManager)
            task_pconn, self.task_cconn = Pipe()
            # Create an event to tell the filter to update it's tasking
            self.task_update_event = Event()
    
            # Start the filter up
            self.p_filt = FilterProcess(recv_pconn, task_pconn, self.done_event, self.task_update_event)
            self.p_filt.start()

            # Start the receiver up
            self.p_recv = SnifferProcess(recv_cconn, self.kb, self.done_event)
            self.p_recv.start()

    def detask(self, uuid):
        res = None
        if uuid in self.tasks:
            res = self.tasks.get(uuid)
            del self.tasks[uuid]
        else:
            return False
        if len(self.tasks) == 0:
            # Time to shut the whole party down, as we don't have any more tasks
            print("Detask has found no remaining tasks, so we're shutting down.")
            self.shutdown()
            #TODO return something to indicate a total shutdown also
        else:
            # We made a change to tasking, let's implement it
            self.__update_filter_tasking()
        return res

    def task(self, uuid, data):
        if uuid in self.tasks:
            # UUIDs should be unique... by their nature.
            return False
        self.tasks[uuid] = data
        self.__update_filter_tasking()
        return True
    
    def display(self, uuid):
        if uuid not in self.tasks:
            return "{0} was not found in tasking.".format(uuid)
        #TODO improve textual output
        return repr(self.tasks.get(uuid))
    
    def shutdown(self):
	print("calling plugin process shutdown function")
        self.done_event.set()
        self.p_recv.join(5)
	if self.p_recv.is_alive():
		self.p_recv.terminate()
        self.p_filt.join(5)
	if self.p_filt.is_alive():
		self.p_filt.terminate()
	print("plugin successfully shutdown")	

    def __update_filter_tasking(self):
        print("Tasking added:", cPickle.dumps(self.tasks).encode('hex'))
        self.task_cconn.send(cPickle.dumps(self.tasks))
        self.task_update_event.set()
'''



