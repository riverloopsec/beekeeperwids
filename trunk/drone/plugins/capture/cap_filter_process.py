'''
The class which is used by launch.py via Multiprocessing to handle
the selection and dispatching of captured packets.
rmspeers 2013 riverloopsecurity.com
'''

import cPickle
from multiprocessing import Process
import urllib2
import json
import os

from killerbeewids.trunk.utils import KBLogUtil

class FilterProcess(Process):
    def __init__(self, pipe, task_pipe, stopevent, task_update_event, drone, parent):
        super(FilterProcess, self).__init__()
        self.pipe = pipe
        self.task_pipe = task_pipe
        self.stopevent = stopevent
        self.taskevent = task_update_event

	self.drone = drone
	self.parent = parent
	self.desc = '{0}.Filter'.format(self.parent)
	self.logutil = KBLogUtil(self.drone)
	self.callbacks = 0

    def do_callback(self, uuid, cburl, pkt):
	# @ryan: below are hacks to bypass formatting/encoding errors, could you look into them?
	# there were some UTF encoding errors for the raw bytes
	pkt['datetime'] = str(pkt['datetime'])
	pkt['bytes'] = "0x" + ''.join( [ "%02X" % ord( x ) for x in pkt['bytes'] ] ).strip()
	pkt[0] = "0x" + ''.join( [ "%02X" % ord( x ) for x in pkt[0] ] ).strip()
	http_headers = {'Content-Type' : 'application/json', 'User-Agent' : 'Drone'}
	post_data_json = json.dumps({'uuid':uuid, 'pkt':pkt})
	post_object = urllib2.Request(cburl, post_data_json, http_headers)
	try:
		response = urllib2.urlopen(post_object)        
		self.logutil.log(self.desc, 'Successful upload task {0} data to: {1}'.format(uuid, cburl), self.pid, 'DEBG')
	except(IOError):
		self.logutil.log(self.desc, 'Failed upload task {0} to: {1}'.format(uuid, cburl), self.pid, 'DEBG')
	self.callbacks += 1

    def run(self):
        '''
        This part runs in a separate process as invoked by Multiprocessing.
        It recieves packets from the SnifferProcess via a pipe, and compares
        them against the data currently in the filters Manager.
        '''
	self.logutil.log(self.desc, 'Started', self.pid)
        tasks = []
        while not self.stopevent.is_set():
            if self.taskevent.is_set():
                # We were notified of a tasking update, so we will hold
                # and read from our tasking pipe to get the updated dictionary.
		self.logutil.log(self.desc, 'Processing tasking update', self.pid)
                pickleTaskDict = self.task_pipe.recv()
                taskDict = cPickle.loads(pickleTaskDict)
                tasks = []
                for uuid, tv in taskDict.items():
                    if 'callback' in tv and 'filter' in tv:
                        tasks.append( (uuid, tv['filter'], tv['callback']) )
                    else:
                        print("Issue with tasking missing required field: {0}: {1}".format(uuid, tv))
                #print "Tasking received:", tasks
                self.taskevent.clear()
            try:
                pkt = self.pipe.recv()
		self.logutil.log(self.desc, 'Received Packet: {0}'.format(pkt['bytes'].encode('hex')), self.pid)
                # Do the basic filtering, and run the callback function on 
                # packets that match:
                for (uuid, filt, cb) in tasks:
                    #print("\tChecking for {0}.".format(filt))
                    # We check to see if the tasking has each test, and
                    # if it does, we see if it meets the defined condition.
                    # If it does not meet a condition, fail out right away.
                    if 'size' in filt:
                        (minB, maxB) = filt['size']
                        pktB = len(pkt['bytes'])
                        if pktB < minB or pktB > maxB:
                            continue
                    if 'fcf' in filt:
                        (mask, val) = filt['fcf']
                        if (unpack('>H', pkt[0:2])[0] & mask) != val:
                            continue
                    # The cases of:
                    # (a) no conditions, aka send all packets, and
                    # (b) unknown condition we don't have coded for
                    # Both come to here and cause a callback to occur
                    self.do_callback(uuid, cb, pkt)
            except IOError as e:
                print "Sniffer pipe on the filter end received an IOError, OK at shutdown:", e
                pass #Should occur if the interupt fires and the pipe is killed.

