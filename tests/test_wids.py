#!/usr/bin/python

from killerbeewids.wids import WIDSClient

c = WIDSClient('127.0.0.1', 8888)
print(c.getStatus())




