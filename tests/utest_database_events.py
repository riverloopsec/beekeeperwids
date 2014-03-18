#!/usr/bin/python

'''
Unit tests for WIDS database backend using snapshot of database ('test.db')
jvazquez 2013 riverloopsecurity.com
'''

import unittest

from beekeeperwids.wids.database import DatabaseHandler, Event

total_count = 36

class TestDatabaseHandlerEvents(unittest.TestCase):
    def setUp(self):
        self.db = DatabaseHandler('wids0')
        #self.db.storeEvent({'module':'UnitTestModule', 'datetime':0, 'name':'TestEvent', 'details':{}, 'uuids':['1234-1234-1234-1234'], 'packets':[0,1,2]})

    def cleanup(self):
        self.db.close()

    def test_event_get_all(self):
        count = self.db.getEvents(count=True)
        self.assertEqual(count, total_count)
        for event in self.db.getEvents():
            print(event.id, event.datetime, event.module, event.name, event.details, event.uuids, event.packets)

    def test_event_get_filter_module(self):
        count = self.db.session.query(Event).filter(Event.module == 'DisassociationStormMonitor').count()
        self.assertEqual(count, 24)

    def test_event_get_mixfilter(self):
        count = self.db.session.query(Event).filter(Event.module == 'DisassociationStormMonitor').filter(Event.name == 'ZigbeeNWKCommandPayload Frame Detected').count()
        self.assertEqual(count, 24)
        


if __name__ == '__main__':
    unittest.main()






