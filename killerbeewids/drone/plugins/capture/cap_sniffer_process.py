'''
The class which is used by launch.py via Multiprocessing to handle
the capturing of packets and passing them to the FilterProcess stage.
rmspeers 2013 riverloopsecurity.com
'''

import os
from multiprocessing import Process

from killerbeewids.utils import KBLogUtil

class SnifferProcess(Process):
    '''
    Takes the KillerBee instance which will be used for sniffing and receives
    packets, feeding each into the given pipe to the FilterProcess, until
    the stopevent fires.
    '''
    def __init__(self, pipe, kb, stopevent, drone, parent):
        super(SnifferProcess, self).__init__()
        self.pipe = pipe
        self.kb   = kb
        self.stopevent = stopevent
        self.desc = '{0}.Sniffer'.format(parent)
        self.logutil = KBLogUtil(drone, 'SnifferProcess', None)

    def run(self):
        '''
        Start receiving and returning packets until the stopevent
        flag is set.
        '''
        self.logutil.log('Initializing')
        self.logutil.log('Turning on interface: {0}'.format(self.kb.device))
        self.kb.sniffer_on()
        while not self.stopevent.is_set():
            recvpkt = self.kb.pnext() #nonbocking
            # Check for empty packet (timeout) and valid FCS
            if recvpkt is not None:# and recvpkt[1]:
                self.logutil.log("Received Frame")
                self.pipe.send(recvpkt)
        self.logutil.log('Turning off interface: {0}'.format(self.kb.device))
        self.kb.sniffer_off()
        self.logutil.log('Terminating Execution')
