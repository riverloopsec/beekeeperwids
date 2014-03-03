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
    validcrc = Column(String(250))
    uuid = Column(String(250))
    pbytes = Column(LargeBinary(150))

    def __init__(self, pktdata):
        self.datetime = int(pktdata.get('datetime'))
        self.source   = str(pktdata.get('location'))
        self.dbm   = str(pktdata['dbm'])
        self.rssi  = int(pktdata['rssi'])
        self.uuid  = str(pktdata['uuid'])
        self.pbytes = base64.b64decode(pktdata['bytes'])
        #self.validcrc = str(pktdata['validcrc'])


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
        returen self.storeElement(Event(event_data))

    def getElement(self, elementClass, filters=[], new=False):
        query = self.session.query(elementClass)
        results = query.all()
        return results

    def getPackets(self, filters=[], new=False):
        return self.getElement(Packet, filters, new)

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


   




