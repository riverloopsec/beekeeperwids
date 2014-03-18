#!/usr/bin/env python

'''
Unit tests for WIDS code for the frontend systems.
rmspeers 2013 riverloopsecurity.com
'''

import unittest

from cap_filters import AllPacketFilter, BasicPacketFilter

frames_beacon_requests = [
    '\x03\x08\xe5\xff\xff\xff\xff\x07\xac\xbf',
    '\x03\x08\xbe\xff\xff\xff\xff\x07\xe8\xd2',
    '\x03\x08\xbf\xff\xff\xff\xff\x07\xc3\xd6']

def sample_callback(pdict, filt):
    print "Got a callback with:", pdict, "from filter", filt

class TestFilterProcess(unittest.TestCase):
    def setUp(self):
        from multiprocessing import Pipe, Event
        from cap_filter_process import FilterProcess

        recv_pconn, self.recv_cconn = Pipe()
        self.done_event = Event()

        self.p_filt = FilterProcess(recv_pconn, self.done_event)
        self.p_filt.start()

    def cleanUp(self):
        self.done_event.set()
        self.p_filt.join()

    def test_filter_add_remove(self):
        subkeyAllPktFilt = self.p_filt.subscribe(AllPacketFilter(), sample_callback)
        self.assertEqual(self.p_filt.subscription_count(), 1)
        self.p_filt.unsubscribe(subkeyAllPktFilt)
        self.assertEqual(self.p_filt.subscription_count(), 0)

    def test_filter_hit_count(self):
        subkeyAllPktFilt = self.p_filt.subscribe(AllPacketFilter(), sample_callback)
        for pktBytes in frames_beacon_requests:
            self.recv_cconn.send({'bytes': pktBytes}) #minimal 'packet' example
        # We're filtering on AllPacketFilter, so we should get a hit count equal
        # to the number of packets we fed in:
        #TODO need to be able to verify result somehow
        #self.assertEqual(self.p_filt.hit_count(subkeyAllPktFilt), len(frames_beacon_requests))
        self.p_filt.unsubscribe(subkeyAllPktFilt)

    def test_filter_fcfcmd(self):
        fcfcmdfilt = BasicPacketFilter()
        fcfcmdfilt.add_fcf_check(0x0300, 0x0300)
        subkey = self.p_filt.subscribe(fcfcmdfilt, sample_callback)
        for pktBytes in frames_beacon_requests:
            self.recv_cconn.send({'bytes': pktBytes}) #minimal 'packet' example
        #TODO need to be able to verify result somehow
        #self.assertEqual(self.p_filt.hit_count(subkey), len(frames_beacon_requests))
        self.p_filt.unsubscribe(subkey)

if __name__ == '__main__':
    unittest.main()
