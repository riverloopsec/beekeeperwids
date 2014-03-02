#!/usr/bin/python

import time
from multiprocessing import Process

class WIDSRuleEngine(Process):

    def __init__(self, rules=[]):
        Process.__init__(self)
        self.rules = rules


    def run(self):
        while True:
            time.sleep(5)
            #print('[DEBUG] RuleEngine running')
