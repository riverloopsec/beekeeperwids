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
import base64
import traceback
from struct import unpack

from killerbeewids.utils import KBLogUtil, dateToMicro

class FilterProcess(Process):
    def __init__(self, pipe, task_queue, stopevent, task_update_event, drone, parent):
        super(FilterProcess, self).__init__()
        self.pipe = pipe
        self.task_queue = task_queue
        self.stopevent = stopevent
        self.taskevent = task_update_event

        self.drone = drone
        self.parent = parent
        self.name = '{0}.Filter'.format(self.parent)
        self.logutil = KBLogUtil(self.drone, self.name, None)
        self.callbacks = 0

    def do_callback(self, uuid, cburl, pkt):
        pkt['uuid'] = uuid
        pkt['datetime'] = dateToMicro(pkt['datetime'])
        pkt['bytes'] = base64.b64encode(pkt['bytes'])
        if 0 in pkt: del pkt[0] # Kill KillerBee's backwards compatible keys
        if 1 in pkt: del pkt[1]
        if 2 in pkt: del pkt[2]
        http_headers = {'Content-Type' : 'application/json', 'User-Agent' : 'Drone'}
        post_data_json = json.dumps({'uuid':uuid, 'pkt':pkt})
        post_object = urllib2.Request(cburl, post_data_json, http_headers)
        try:
            response = urllib2.urlopen(post_object)
            self.logutil.debug('Successful Data Upload task {0} data to: {1}'.format(uuid, cburl))
        except(IOError):
            self.logutil.debug('Failed Data Upload task {0} to: {1}'.format(uuid, cburl))
        self.callbacks += 1

    def run(self):
        '''
        This part runs in a separate process as invoked by Multiprocessing.
        It recieves packets from the SnifferProcess via a pipe, and compares
        them against the data currently in the filters Manager.
        '''
        self.logutil.log('Started')
        tasks = []
        while not self.stopevent.is_set():
        
            # check if there are new tasks and update
            while not self.task_queue.empty():
                self.logutil.debug('Detected Tasking Update in Queue')
                tasks = []
                pickleTaskDict = self.task_queue.get_nowait()
                for uuid,data in cPickle.loads(pickleTaskDict).items():
                    tasks.append( (uuid, data['filter'], data['callback']) )
                self.task_queue.task_done()
                self.logutil.log('Tasking Updated ({0} tasks total)'.format(len(tasks)))
           
            # get packet from sniffer and match against tasked filters 
            try:
                pkt = self.pipe.recv()
                self.logutil.debug('Received Packet: {0}'.format(pkt['bytes'].encode('hex')))
                self.logutil.dev('Filtering against {0} tasks ({1})'.format(len(tasks), list((x[0] for x in tasks))))
                # Do the basic filtering, and run the callback function on packets that match
                for (uuid, filt, cb) in tasks:
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
                        if (unpack('>H', pkt['bytes'][0:2])[0] & mask) != val:
                            continue
                    if 'byteoffset' in filt:
                        (offset, mask, val) = filt['byteoffset']
                        if offset >= len(pkt['bytes']):
                            continue
                        if (unpack('B', pkt['bytes'][offset])[0] & mask) != val:
                            continue
                    # The cases of:
                    # (a) no conditions, aka send all packets, and
                    # (b) unknown condition we don't have coded for
                    # Both come to here and cause a callback to occur
                    self.logutil.debug('Matched Packet against task: {0}'.format(uuid))
                    self.do_callback(uuid, cb, pkt)
            except Exception as e:
                traceback.print_exc()
                print "Sniffer pipe on the filter end received an IOError, OK at shutdown:", e
