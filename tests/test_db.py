#!/usr/bin/python

from killerbeewids.wids.database import *


db = DatabaseHandler('kbwids.db')
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


getAllPackets()

print("========")

getNewPackets()

print("========")

getPackets([('id','>',1), ('rssi','>',78)])






