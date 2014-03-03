#!/usr/bin/python

from killerbeewids.wids.database import *


db = DatabaseHandler('wids0')
dataType = Packet


u1 = '03ff76a6-51dc-4bea-8eaf-1d82bbdf2a5b'

#for packet in db.session.query(Packet).filter('uuid == "03ff76a6-51dc-4bea-8eaf-1d82bbdf2a5b"').all():
#    print(packet.uuid)

for packet in db.getPackets(filterList=[('rssi','>','78')], uuidList=[u1]):
    print(packet.uuid, packet.rssi)


for packet in db.getPackets(filterList=('rssi','>','78'), uuidList=[u1]):
    print(packet.uuid, packet.rssi)



