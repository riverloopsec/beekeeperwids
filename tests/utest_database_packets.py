#!/usr/bin/python

'''
Unit tests for WIDS database backend using snapshot of database ('test.db')
jvazquez 2013 riverloopsecurity.com
'''

import unittest

from killerbeewids.wids.database import DatabaseHandler


t1_uuid  = 'f88d3cac-7136-4a31-9153-a4b1605e1b90'
t1_count = 219
t2_uuid  = '4980a309-7307-409c-9ebd-f39447fdb336'
t2_count = 20
t3_uuid  = '33a05151-6890-45eb-aa7d-c21e9910d4c1'
t3_count = 43
t4_uuid  = '2e9f0929-b2da-4094-bb28-56861915f12c'
t4_count = 11
t5_uuid  = 'a93c2bce-f955-4031-bb08-f312b2c8661a'
t5_count = 80
total_count = 387
rssi_gt_78 = 164
rssi_eq_78 = 178
rssi_lt_78 = 45

class TestDatabaseHandlerPackets(unittest.TestCase):
    def setUp(self):
        self.db = DatabaseHandler('packet', path='./')

    def cleanup(self):
        self.db.close()

    def test_packet__get_all(self):
        count = self.db.getPackets(count=True)
        self.assertEqual(count, total_count)

    def test_packet_get_new_(self):
        # query packets WITHOUT new flag
        packets_1 = self.db.getPackets(maxcount=100)
        index_1a = packets_1[0].id
        index_1b = packets_1[-1].id
        packets_2 = self.db.getPackets(maxcount=100)
        index_2a = packets_2[0].id
        index_2b = packets_2[-1].id
        self.assertEqual(index_1a, 1)
        self.assertEqual(index_1b, 100)
        self.assertEqual(index_2a, 1)
        self.assertEqual(index_2b, 100)
        # query packets WITH new flag
        packets_1 = self.db.getPackets(maxcount=100, new=True)
        index_1a = packets_1[0].id
        index_1b = packets_1[-1].id
        packets_2 = self.db.getPackets(maxcount=100, new=True)
        index_2a = packets_2[0].id
        index_2b = packets_2[-1].id
        self.assertEqual(index_1a, 1)
        self.assertEqual(index_1b, 100)
        self.assertEqual(index_2a, 101)
        self.assertEqual(index_2b, 200)

    def test_packet_get_maxcount_(self):
        count = self.db.getPackets(maxcount=100, count=True)
        self.assertEqual(count, 100)

    def test_packet_get_t1_count(self):
        count = self.db.getPackets(uuidFilterList=[t1_uuid], count=True)    
        self.assertEqual(count, t1_count)

    def test_packet_get_t2_count(self):
        count = self.db.getPackets(uuidFilterList=[t2_uuid], count=True)    
        self.assertEqual(count, t2_count)

    def test_packet_filter_rssi_gt(self):
        count = self.db.getPackets(valueFilterList=[('rssi','>',78)], count=True)
        self.assertEqual(count, rssi_gt_78)

    def test_packet_filter_rssi_eq(self):
        count = self.db.getPackets(valueFilterList=[('rssi','==',78)], count=True)
        self.assertEqual(count, rssi_eq_78)

    def test_packet_filter_rssi_lt(self):
        count = self.db.getPackets(valueFilterList=[('rssi','<',78)], count=True)
        self.assertEqual(count, rssi_lt_78)

    def test_packet_filter_datetime(self):
        pass

    def test_packet_mix_filters(self):
        count = self.db.getPackets(valueFilterList=[('rssi','>',78)], uuidFilterList=[t1_uuid], count=True)
        self.assertEqual(count, 76)
        

class TestDatabaseHandlerEvents(unittest.TestCase):
    def setUp(self):
        self.db = DatabaseHandler('event2', path='./')
        self.db.storeEvent({'module':'UnitTestModule', 'datetime':0, 'name':'TestEvent', 'details':{}, 'uuids':['1234-1234-1234-1234'], 'packets':[0,1,2]})

    def cleanup(self):
        self.db.close()

    def test_event_get_all(self):
        events = self.db.getEvents()

        for event in events:
            print(event.id, event.datetime, event.module, event.name, event.details, event.uuids, event.packets)


if __name__ == '__main__':
    unittest.main()






