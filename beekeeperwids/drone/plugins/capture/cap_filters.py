'''
Filters to select on captured packets.
rmspeers 2013 riverloopsecurity.com
'''

from struct import unpack

class FilterArgumentError(Exception):
    pass

def _fcf_check(pkt, mask, val):
    fcf = unpack('>H', pkt[0:2])[0]
    fcfm = fcf & mask
    return (fcfm == val)

class BasicPacketFilter():
    def __init__(self):
        self.checkfuncs = []
    def add_fcf_check(self, mask, val):
        if 0 > mask or mask > 0xffff or 0 > val or val > 0xffff:
            raise FilterArgumentError("The FCF mask {0:x} with value {1:x} is not valid.".format(mask, val))
        # TODO actually parse the packet and mask and check the FCF!
        self.checkfuncs.append(lambda pkt: True) #(unpack('>H', pkt[0:2])[0] & mask) == val
    def add_length_range(self, minl, maxl):
        if minl < 0 or maxl > 127 or minl > maxl:
            raise FitlerArgumentError("The length range {0} to {1} is not valid.".format(minl, maxl))
        self.checkfuncs.append(lambda pkt: (minl <= len(pkt) <= maxl))
    def add_custom_checkfunc(self, checkfunc):
        #TODO validate the function takes a single argument, pkt, and returns a boolean
        self.checkfuncs.append(checkfunc)
    def decide_pkt(self, pkt):
        '''Check a packet against all parameters in this filter.'''
        for checkfunc in self.checkfuncs:
            if checkfunc(pkt) == False:
                return False
        return True
    def __repr__(self):
        return '{0}[{1}]'.format(self.__class__.__name__, ','.join(self.checkfuncs))

# Some common filters:

class AllPacketFilter(BasicPacketFilter):
    def add_fcf_check(self, mask, val):     raise NotImplemented()
    def add_length_range(self, minl, maxl): raise NotImplemented()
    def add_custom_checkfunc(self, checkfunc): raise NotImplemented()
    def decide_pkt(self, pkt):              return True

class FcfBeaconPacketFilter(BasicPacketFilter):
    def __init__(self):
        BasicPacketFilter.__init__(self)
        self.add_fcf_check(0x0300, 0x0000)

class FcfDataPacketFilter(BasicPacketFilter):
    def __init__(self):
        BasicPacketFilter.__init__(self)
        self.add_fcf_check(0x0300, 0x0100)

class FcfAckPacketFilter(BasicPacketFilter):
    def __init__(self):
        BasicPacketFilter.__init__(self)
        self.add_fcf_check(0x0300, 0x0200)

class FcfCmdPacketFilter(BasicPacketFilter):
    def __init__(self):
        BasicPacketFilter.__init__(self)
        self.add_fcf_check(0x0300, 0x0300)

#BeaconRequestFilter(BasicPacketFilter):
