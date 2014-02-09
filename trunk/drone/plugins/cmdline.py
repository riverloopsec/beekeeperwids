#!/usr/bin/env python

'''
Takes commands to deliver sniffed packets, or data segments from them,
back to the requestor on the backend.
rmspeers 2013 riverloopsecurity.com
'''

import argparse
import signal
import sys

from killerbee import *

from capture import CapturePlugin

CaptureObj = None

def interrupt(signum, frame):
    global CaptureObj
    if CaptureObj is not None:
        CaptureObj.shutdown()
        #CaptureObj.detask('TEST')

if __name__ == '__main__':
    # Command-line arguments
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-i', '--iface', '--dev', action='store', dest='devstring', default=None)
    parser.add_argument('-c', '--channel', action='store', type=int, required=True)
    args = parser.parse_args()

    signal.signal(signal.SIGINT, interrupt)

    try:
        kb = KillerBee(device=args.devstring)
    except Exception as e:
        #TODO tune exceptions and cleanup instance/device as needed
        print("KillerBee instantiation failure: ({0}).".format(e))
	sys.exit(-1)
    print "KillerBee instance to use is:", kb
    
    # Start our capture on the given channel
    CaptureObj = CapturePlugin( [kb], {'channel':args.channel} )
    if not CaptureObj.status:
    	print "Result of starting CapturePlugin was", CaptureObj.status
	sys.exit(-1)
    
    # Put some tasking in here
    sampleTaskData = {'callback':'localhost:8080',
                      'filter'  :{} }
    CaptureObj.task('TEST', sampleTaskData)
    print "Added the TEST task."

