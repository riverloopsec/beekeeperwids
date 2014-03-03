#!/usr/bin/python

from killerbeewids.wids.database import *

print('stuff')

db = DatabaseHandler('wids0')
dataType = Packet


def getPackets(queryFilter):

    print(queryFilter)

    query = db.session.query(dataType)

    for key,operator,value in queryFilter:
        print(key,operator,value)
        query = query.filter('{0}{1}{2}'.format(key,operator,value))

    results = query.all()

    for packet in results:
        packet.display()



def getNewPackets():
    packets = db.session.query(Packet).all()
    time = packets[0].datetime

    query = db.session.query(dataType)
    query = query.filter('datetime>{0}'.format(time))
    query = query.filter('rssi>78')
    results = query.all()

    for packet in results:
        packet.display()


def getAllPackets():

    for packet in db.session.query(Packet).all():
        packet.display()

u1 = '03ff76a6-51dc-4bea-8eaf-1d82bbdf2a5b'

for packet in db.session.query(Packet).filter('uuid == "03ff76a6-51dc-4bea-8eaf-1d82bbdf2a5b"').all():
    print(packet.uuid)




