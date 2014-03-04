#!/usr/bin/python

'''
Unit tests for WIDS database backend using snapshot of database ('test.db')
jvazquez 2013 riverloopsecurity.com
'''

import unittest

from killerbeewids.wids.database import DatabaseHandler


class TestDatabaseHandlerEvents(unittest.TestCase):
    def setUp(self):
        self.db = DatabaseHandler('wids0')
        #self.db.storeEvent({'module':'UnitTestModule', 'datetime':0, 'name':'TestEvent', 'details':{}, 'uuids':['1234-1234-1234-1234'], 'packets':[0,1,2]})

    def cleanup(self):
        self.db.close()

    def test_event_get_all(self):
        events = self.db.getEvents()

        for event in events:
            print(event.id, event.datetime, event.module, event.name, event.details, event.uuids, event.packets)


if __name__ == '__main__':
    unittest.main()






