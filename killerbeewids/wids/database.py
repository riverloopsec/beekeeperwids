#!/usr/bin/python

import os
import sys
import base64
import traceback
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, PickleType, create_engine, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from killerbeewids.utils import KB_CONFIG_PATH
Base = declarative_base()


class Event(Base):
    __tablename__ = 'event'
    id = Column(Integer, primary_key=True)
    datetime = Column(Integer())
    module   = Column(String(100))
    name     = Column(String(100))
    details  = Column(PickleType())

    def __init__(self, event_data):
        self.datetime = int(event_data.get('datetime'))
        self.module   = str(event_data.get('module'))
        self.name     = str(event_data.get('name'))
        self.details  = event_data.get('details')


class Packet(Base):
    __tablename__ = 'packet'
    id = Column(Integer, primary_key=True)
    source   = Column(String(250))
    datetime = Column(Integer())
    dbm      = Column(Integer)
    rssi     = Column(Integer())
    validcrc = Column(Boolean)
    uuid     = Column(String(250))
    pbytes   = Column(LargeBinary(150))

    def __init__(self, pktdata):
        self.datetime = int(pktdata.get('datetime'))
        self.source   = str(pktdata.get('location'))
        self.dbm      = str(pktdata['dbm'])
        self.rssi     = int(pktdata['rssi'])
        self.uuid     = str(pktdata['uuid'])
        self.pbytes   = base64.b64decode(pktdata['bytes'])
        self.validcrc = pktdata['validcrc']

    # TODO - modify this so that self.uuid is a list not a single string
    def checkUUID(self, uuidList):
        for uuid in uuidList:
            if uuid == self.uuid:
                return True
        return False

    


class DatabaseHandler:
    def __init__(self, database, path=KB_CONFIG_PATH):
        databasefile = "sqlite:///{0}/{1}.db".format(path, database)
        self.engine = create_engine(databasefile, echo=False)
        if not os.path.isfile(database):
            self.createDB()
        self.session = sessionmaker(bind=self.engine)()
        self.packet_index = 0
        self.event_index = 0

    def createDB(self):
        Base.metadata.create_all(self.engine)

    def close(self):
        #TODO - how to close a connection?
        pass

    def storeElement(self, element):
        try:
            self.session.add(element)
            self.session.commit()
            return True
        except Exception:
            traceback.print_exc()
            return False

    def storePacket(self, packet_data):
        return self.storeElement(Packet(packet_data))

    def storeEvent(self, event_data):
        return self.storeElement(Event(event_data))


    #TODO - add functionality to search by date/times
    #TODO - add functionality to search for byte patterns

    def getPackets(self, valueFilterList=[], uuidFilterList=[], new=False, maxcount=0, count=False):
        # verify parameters are valid
        if not type(valueFilterList) is list or not type(uuidFilterList) is list or not type(maxcount) is int:
            raise Exception("'filterList' and 'uuidList' must be type lists")

        # prepare base query
        query = self.session.query(Packet)

        # apply new packets filter
        if new: query = query.filter('id > {0}'.format(self.packet_index))

        # apply value filters
        for key,operator,value in valueFilterList:
            query = query.filter('{0}{1}{2}'.format(key,operator,value))

        # apply maxcount filter
        if maxcount > 0: query = query.limit(maxcount)

        # issue query and get results
        results = query.all()

        # if new packets are being queried, save the index
        if new: self.packet_index = results[-1].id

        # filter packets by uuid (after query)
        # it might be possible to perform this in the query itself for now,
        # but probably not when we have lists of uuids in the packet
        # TODO - look into above
        temp = results
        results = []
        if len(uuidFilterList) > 0:
            for packet in temp:
                if packet.checkUUID(uuidFilterList):
                    results.append(packet)    
        else:
            results = temp

        # return actual packets or packet count
        if not count:
            return results
        else:
            return len(results) 


    def getEvents(self, analyticModule=None, valuefilterList=[], new=False, maxcount=0, count=False):
        # verify parameters are valid
        if not type(valueFilterList) is list or not type(uuidFilterList) is list or not type(maxcount) is int:
            raise Exception("'filterList' and 'uuidList' must be type lists")

        # prepare base query
        query = self.session.query(Event)

        # apply new packets filter
        if new: query = query.filter('id > {0}'.format(self.event_index))

        # apply value filters
        for key,operator,value in valueFilterList:
            query = query.filter('{0}{1}{2}'.format(key,operator,value))

        # apply maxcount filter
        if maxcount > 0: query = query.limit(maxcount)

        # issue query and get results
        results = query.all()

        # if new packets are being queried, save the index
        if new: self.event_index = results[-1].id

        # return actual packets or packet count
        if not count:
            return results
        else:
            return len(results) 

   




