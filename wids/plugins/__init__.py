#!/usr/bin/python

from multiprocessing import Process

import killerbeewids.wids.database as db
from killerbeewids.utils import KBLogUtil

# TODO - incorporate shutdown event & implement proper shutdown sequence
# TODO - implement proper evenet generation mechanism

class AnalyticPlugin(Process):

        def __init__(self, config, name):
                Process.__init__(self)
                self.name = name
                self.config = config
                self.desc = None
                self.logutil = KBLogUtil(self.config.settings.get('appname'))
                self.database = db.DatabaseHandler(self.config.settings.get('database'))

                self.PACKETS_ALL = {}
                self.lastPacketTime = None


        def taskDrone(self, uuid, plugin, channel, parameters):
                self.database.storeTaskRequest(uuid, plugin, channel, parameters)

        def detaskDrone(self, uuid, plugin, channel, parameters):
                pass

        def getPackets(self, queryFilter):
                return self.database.getPackets(queryFilter)

        def getNewPackets(self, queryFilter):
                # records the last packet id and only searches for new packets
                try:
                        packets = self.database.session.query(Packet).all()
                        return packets
                except Exception as e:
                        print("ERROR - Failed to Get Packets")
                        print(e)
                        return None

        def getEvents(self):
                pass

        def registerEvent(self):
                pass

        def terminate(self):
                self.detaskAll()
                self.shutdown()
                '''
                this method can be call externally to terminate the module
                '''

        def run(self):
                '''
                overwrite this method
                '''
                pass

        def detaskAll(self):
                '''
                this function will detask all the running tasks on the drone prior to shutdown
                '''

        def shutdown(self):
                '''
                overwrite this methods
                '''
                pass


