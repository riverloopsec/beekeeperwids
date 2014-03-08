# Plugin for drone to preform raw PCAP capture, with optional filters applied.

import cPickle
import time, os
from multiprocessing import Pipe, Event, Manager, JoinableQueue

from cap_filter_process import FilterProcess
from cap_sniffer_process import SnifferProcess

from killerbeewids.drone.plugins import BaseDronePlugin


class CapturePlugin(BaseDronePlugin):
    def __init__(self, interfaces, channel, drone):
        BaseDronePlugin.__init__(self, interfaces, channel, drone, 'CapturePlugin.{0}'.format(channel))
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
        self.task_queue = JoinableQueue()
        # Start the filter up
        self.p_filt = FilterProcess(recv_pconn, self.task_queue, self.done_event, self.task_update_event, self.drone, self.name)
        self.p_filt.start()
        self.logutil.log('Launched FilterProcess ({0})'.format(self.p_filt.pid))
        self.childprocesses.append(self.p_filt)
        # Start the receiver up
        self.p_recv = SnifferProcess(recv_cconn, self.kb, self.done_event, self.drone, self.name)
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
        #return res
        return True

    def __update_filter_tasking(self):
        self.logutil.log('Sending Task Updates to FilterProcess')
        self.task_queue.put_nowait(cPickle.dumps(self.tasks))
      
