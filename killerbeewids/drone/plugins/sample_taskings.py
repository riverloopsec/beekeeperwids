# These are some sample taskings for what the CapturePlugin may get tasked
# with in different scenarios.
'''
from uuid import uuid1
get_uuid = lambda: uuid1().bytes


# All packets
ap = {get_uuid():
        {'callback': 'localhost:8080/app/fullcap/',
         'filter'  : {}
     }}

# Beacon frames
bp = {get_uuid():
        {'callback': 'localhost:8080/app/nwkjoin/',
         'filter'  : {
            'fcf': (0x0300, 0x0000)
            #The mask to apply, and then the value to compare with
          }
     }}

# Command frames, command ID = 0x07 (Beacon Request)
br = {'callback': 'localhost:8080/app/beconreq/',
      'filter'  : {
         'fcf': (0x0300, 0x0300),
         'byteoffset': (7, 0xff, 0x07)
      }
     }

# Frames of length 100 to 104
lp = {get_uuid():
        {'callback': 'localhost:8080/app/heartbeats/',
         'filter'  : {
            'size': (100, 104)
            #In bytes, the min and max number allowed in the packet, inclusive
            #Use None to indicate no restriction on one end
          }
     }}

# Ack frames
ak = {get_uuid():
        {'callback': 'localhost:8080/app/ackforging/',
         'filter'  : {
            'fcf': (0x0300, 0x0200)
            #The mask to apply, and then the value to compare with
          }
     }}
'''

import json


print(json.dumps({'callback': 'localhost:8080/app/fullcap/','filter'  : {}}))
