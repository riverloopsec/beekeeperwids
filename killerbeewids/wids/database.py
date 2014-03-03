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
    source = Column(String(250))
    data = Column(String(250))

    def __init__(self, source, data):
        self.source = source
        self.data = data


class Packet(Base):
    __tablename__ = 'packet'
    id = Column(Integer, primary_key=True)
    source = Column(String(250))
    datetime = Column(Integer())
    dbm = Column(Integer)
    rssi = Column(Integer())
    validcrc = Column(Boolean)
    uuid = Column(String(250))
    pbytes = Column(LargeBinary(150))

    def __init__(self, pktdata):
        self.datetime = int(pktdata.get('datetime'))
        self.source   = str(pktdata.get('location'))
        self.dbm      = str(pktdata['dbm'])
        self.rssi     = int(pktdata['rssi'])
        self.uuid     = str(pktdata['uuid'])
        self.pbytes   = base64.b64decode(pktdata['bytes'])
        self.validcrc = pktdata['validcrc']

    def checkUUID(self, uuidList):
        # check if any of the UUIDs in the provided list match the Packet's UUIDs list
        # TODO - modify this so that self.uuid is a list not a single string
        for uuid in uuidList:
            #if uuid in self.uuid:
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

    def getPackets(self, filterList=[], uuidList=[], new=False, maxcount=0, count=False):
        # verify parameters are valid
        if not type(filterList) is list or not type(uuidList) is list or not type(maxcount) is int:
            raise Exception("'filterList' and 'uuidList' must be type lists")

        # prepare base query
        query = self.session.query(Packet)

        # filtery by packet values
        for key,operator,value in filterList:
            query = query.filter('{0}{1}{2}'.format(key,operator,value))

        # apply maxcount limit
        if maxcount > 0: query = query.limit(maxcount)

        # issue query and get results
        results = query.all()

        # filter packets by uuid (after query)
        temp = results
        results = []
        if len(uuidList) > 0:
            for packet in temp:
                if packet.checkUUID(uuidList):
                    results.append(packet)    
        else:
            results = temp


        # return actual packets or packet count
        if not count:
            return results
        else:
            return len(results) 

    def getEvents(self, filters=[], new=False):
        return self.getElement(Event, filters, new)


    '''

    def getNewPackets(self, queryFilter=[], uuid=None): 
        queryFilter.append(('id','>',self.lastPacketIndex)) 
        results = self.getPackets(queryFilter, uuid) 
        if len(results) > 0: 
            self.lastPacketIndex = results[-1].id 
        return results 

    def getPackets(self, queryFilter=[], uuid=None, new=False):
        query = self.database.session.query(Packet)
        if not uuid == None:
            query.filter('uuid == "{0}"'.format(uuid))
        for key,operator,value in queryFilter:
            #print(key,operator,value)
            query = query.filter('{0}{1}{2}'.format(key,operator,value))
        results = query.all()
        return results
    '''


   




