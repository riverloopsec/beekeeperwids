#!/usr/bin/python

import time
from multiprocessing import Process
from killerbeewids.wids.database import DatabaseHandler
from killerbeewids.wids.client import WIDSClient
from killerbeewids.utils import KBLogUtil

class WIDSRuleEngine(Process):

    def __init__(self, config):
        Process.__init__(self)
        self.name = 'RuleEngine'
        self.config = config
        self.database = DatabaseHandler(self.config.name)
        self.logutil = KBLogUtil(self.config.name, self.name)
        self.wids = WIDSClient(self.config.server_ip, self.config.server_port)
        self.active = None

    def run(self):
        self.logutil.log('Starting Execution')        
        self.active = True

        while self.active:
            time.sleep(20)
            self.logutil.log('Checking for Events')

            events = self.database.getEvents()
            
            #for event in events:
            #    print(event.id, event.module, event.name)

        self.logutil.log('Terminating Execution')

    '''
    example: dissasoc storm rule (if 3 events are generated, generate an alert)
    

    def evaluateRule(self, rule):
        for condition in rule.conditions:
            if not condition:
                return 
        for action in rule.actions:
            action.execute()
    '''


    def shutdown(self):
        self.active = False
        self.terminate()

