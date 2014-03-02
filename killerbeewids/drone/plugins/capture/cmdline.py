#!/usr/bin/env python

'''
Takes commands to deliver sniffed packets, or data segments from them,
back to the requestor on the backend.
rmspeers 2013 riverloopsecurity.com
'''

import argparse
import signal

from killerbee import *

from . import CapturePlugin

CaptureObj = None

def interrupt(signum, frame):
    global CaptureObj
    CaptureObj.detask('TEST')

if __name__ == '__main__':
    # Command-line arguments
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-i', '--iface', '--dev', action='store', dest='devstring')
    parser.add_argument('-c', '--channel', action='store', type=int, required=True)
    args = parser.parse_args()

    signal.signal(signal.SIGINT, interrupt)

    try:
        kb = KillerBee(device=args.devstring)
    except Exception as e:
        #TODO tune exceptions and cleanup instance/device as needed
        print("KillerBee instantiation failure: ({0}).".format(e))
    print "KillerBee instance to use is:", kb
    
    # Start our capture on the given channel
    CaptureObj = CapturePlugin( [kb], {'channel':args.channel} )
    print "Result of starting CapturePlugin was", CaptureObj.status
    
    # Put some tasking in here
    sampleTaskData = {'callback':'localhost:8080',
                      'filters' :[] }
    CaptureObj.task('TEST', sampleTaskData)

