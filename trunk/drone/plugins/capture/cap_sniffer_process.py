'''
The class which is used by launch.py via Multiprocessing to handle
the capturing of packets and passing them to the FilterProcess stage.
rmspeers 2013 riverloopsecurity.com
'''

from multiprocessing import Process

class SnifferProcess(Process):
    '''
    Takes the KillerBee instance which will be used for sniffing and receives
    packets, feeding each into the given pipe to the FilterProcess, until
    the stopevent fires.
    '''
    def __init__(self, pipe, kb, stopevent):
        super(SnifferProcess, self).__init__()
        self.pipe = pipe
        self.kb   = kb
        self.stopevent = stopevent
    def run(self):
        '''
        Start receiving and returning packets until the stopevent
        flag is set.
        '''
        self.kb.sniffer_on()
        while not self.stopevent.is_set():
            recvpkt = self.kb.pnext() #nonbocking
            # Check for empty packet (timeout) and valid FCS
            if recvpkt is not None:# and recvpkt[1]:
                print "SnifferProcess received frame."
                self.pipe.send(recvpkt)
        self.kb.sniffer_off()

