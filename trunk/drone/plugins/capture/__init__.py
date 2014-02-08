# Plugin for drone to preform raw PCAP capture, with optional filters applied.

from multiprocessing import Pipe, Event, Manager

from cap_filter_process import FilterProcess
from cap_sniffer_process import SnifferProcess

class CapturePlugin(object):
    def __init__(kblist, data):
        '''
        We are given a list of KillerBee() class objects for the interfaces
        we can use (in this case capture on), and a data object of other
        data we may need (in this case the channel number).
        Check the status flag that this sets to see if initialization 
        was successful in the calling function.
        '''
        manager = Manager()
        self.tasks  = manager.dict() #dictionary is UUID: data
        self.status = True
        if len(kblist) != 1 or 'channel' not in data:
            self.status = False
        else:
            self.channel = data.get('channel')
            self.kb = kblist[0]
            try:
                self.kb.set_channel(channel)
            except Exception as e:
                #TODO tune exceptions and cleanup instance/device as needed
                print("KillerBee instantiation failure: ({0}).".format(e))
                self.status = False
        if self.status:
            print "KillerBee instance to use is:", self.kb

            # Pipe from the receiver to the filter module
            recv_pconn, recv_cconn = Pipe()
            # Create an event to signal when we want to shut down
            self.done_event = Event()
            # Create an event to tell the filter to update it's tasking
            self.task_update_event = Event()
    
            # Start the filter up
            self.p_filt = FilterProcess(recv_pconn, self.tasks, self.done_event, self.task_update_event)
            self.p_filt.start()

            # Start the receiver up
            self.p_recv = SnifferProcess(recv_cconn, kb, self.done_event)
            self.p_recv.start()
            
    def detask(uuid, data):
        res = None
        if uuid in self.tasks:
            res = self.tasks.get(uuid)
            del self.tasks[uuid]
        else:
            return False
        if len(self.tasks) == 0:
            # Time to shut the whole party down, as we don't have any more tasks
            self.done_event.set()
            self.p_recv.join()
            self.p_filt.join()
            #TODO return something to indicate a total shutdown also
        else:
            # We made a change to tasking, let's commit it
            self.task_update_event.set()
        return res

    def task(uuid, data):
        if uuid in self.tasks:
            # UUIDs should be unique... by their nature.
            return False
        self.tasks[uuid] = data
        self.task_update_event.set()
        return True
    
    def display(uuid):
        if uuid not in self.tasks:
            return "{0} was not found in tasking.".format(uuid)
        #TODO improve textual output
        return repr(self.tasks.get(uuid))
    
