'''
The class which is used by launch.py via Multiprocessing to handle
the selection and dispatching of captured packets.
rmspeers 2013 riverloopsecurity.com
'''

from multiprocessing import Process

class FilterProcess(Process):
    def __init__(self, pipe, tasks, stopevent, task_update_event):
        super(FilterProcess, self).__init__()
        self.pipe = pipe
        self.tasks = tasks  #Manager-based dictionary containing tasking
        self.stopevent = stopevent
        self.taskevent = task_update_event

    def run(self):
        '''
        This part runs in a separate process as invoked by Multiprocessing.
        It recieves packets from the SnifferProcess via a pipe, and compares
        them against the data currently in the filters Manager.
        '''
        while not self.stopevent.is_set():
            if self.taskevent.is_set():
                # Update our concept of tasking
                #TODO
                self.taskevent.clear()
            try:
                pkt = self.pipe.recv()
                print "FilterProcess received:", pkt
                # Do the basic filtering, and run the callback function on 
                # packets that match:
                for taskitem in self.tasks():
                    #print "\tChecking filter", filt
                    #TODO take action, filter, callback
                    print("\tChecking for {0}.".format(taskitem))
            except IOError:
                print "Pipe succombed to an IOError, OK at shutdown."
                pass #Should occur if the interupt fires and the pipe is killed.

