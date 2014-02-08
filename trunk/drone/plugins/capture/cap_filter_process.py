'''
The class which is used by launch.py via Multiprocessing to handle
the selection and dispatching of captured packets.
rmspeers 2013 riverloopsecurity.com
'''

import cPickle
from multiprocessing import Process

class FilterProcess(Process):
    def __init__(self, pipe, task_pipe, stopevent, task_update_event):
        super(FilterProcess, self).__init__()
        self.pipe = pipe
        self.task_pipe = task_pipe
        self.stopevent = stopevent
        self.taskevent = task_update_event

    def run(self):
        '''
        This part runs in a separate process as invoked by Multiprocessing.
        It recieves packets from the SnifferProcess via a pipe, and compares
        them against the data currently in the filters Manager.
        '''
        tasks = {}
        while not self.stopevent.is_set():
            if self.taskevent.is_set():
                # We were notified of a tasking update, so we will hold
                # and read from our tasking pipe to get the updated dictionary.
                print "Getting a tasking update..."
                pickleTaskDict = self.task_pipe.recv()
                tasks = cPickle.loads(pickleTaskDict)
                print "Tasking received:", tasks
                self.taskevent.clear()
            try:
                pkt = self.pipe.recv()
                print "FilterProcess received:", pkt['bytes'].encode('hex')
                # Do the basic filtering, and run the callback function on 
                # packets that match:
                for taskitem in tasks.items():
                    #print "\tChecking filter", filt
                    #TODO take action, filter, callback
                    print("\tChecking for {0}.".format(taskitem))
            except IOError as e:
                print "Sniffer pipe on the filter end received an IOError, OK at shutdown:", e
                pass #Should occur if the interupt fires and the pipe is killed.

