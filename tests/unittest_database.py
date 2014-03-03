#!/usr/bin/python

'''
Unit tests for WIDS database backend using snapshot of database ('test.db')
jvazquez 2013 riverloopsecurity.com
'''

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

import unittest

from killerbeewids.wids.database import DatabaseHandler

class TestDatabaseHandler(unittest.TestCase):
    def setUp(self):
        self.db = DatabaseHandler('test', path='./')

    def cleanup(self):
        self.db.close()

    def test_get_all_packets(self):
        count = self.db.getPackets(count=True)
        self.assertEqual(count, total_count)

    def test_get_new_packets(self):
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

    def test_get_maxcount_packets(self):
        count = self.db.getPackets(maxcount=100, count=True)
        self.assertEqual(count, 100)

    def test_get_t1_count(self):
        count = self.db.getPackets(uuidList=[t1_uuid], count=True)    
        self.assertEqual(count, t1_count)

    def test_get_t2_packets(self):
        count = self.db.getPackets(uuidList=[t2_uuid], count=True)    
        self.assertEqual(count, t2_count)

    def test_filter_rssi_gt(self):
        count = self.db.getPackets(filterList=[('rssi','>',78)], count=True)
        self.assertEqual(count, rssi_gt_78)

    def test_filter_rssi_eq(self):
        count = self.db.getPackets(filterList=[('rssi','==',78)], count=True)
        self.assertEqual(count, rssi_eq_78)

    def test_filter_rssi_lt(self):
        count = self.db.getPackets(filterList=[('rssi','<',78)], count=True)
        self.assertEqual(count, rssi_lt_78)

    def test_filter_dbm(self):
        pass

    def test_filter_source(self):
        pass

    def test_filter_datetime(self):
        pass

    def test_filter_bytes(self):
        pass

    def test_mix_filters_1(self):
        #count = self.db.getPackets(filterList=[('rssi','>',78))
        pass

    def test_mix_filters_2(self):
        pass

    def test_mix_filters_3(self):
        pass


if __name__ == '__main__':
    unittest.main()




#for packet in db.session.query(Packet).filter('uuid == "03ff76a6-51dc-4bea-8eaf-1d82bbdf2a5b"').all():
#    print(packet.uuid)

#for packet in db.getPackets(filterList=[('rssi','>','78')], uuidList=[u1]):
#    print(packet.uuid, packet.rssi)




