#!/usr/bin/python

import time
from datetime import datetime
from multiprocessing import Process
from killerbeewids.wids.database import DatabaseHandler, Event
from killerbeewids.wids.client import WIDSClient
from killerbeewids.utils import KBLogUtil, dateToMicro

DEV_DEBUG=True

class RuleDissasocAttack:

    def __init__(self):
        self.rule_id = 'RD-10384'
        self.name = 'Dissasociation Attack Alert'
        self.event_conditions = [('DisassociationStormMonitor', 'ZigbeeNWKCommandPayload Frame Detected', 1)]
        self.execute_actions  = [('GenerateAlert', {'name':'Dissasociation Attack Alert'})]
        self.event_index = 0

# TODO - load/unload rules dynamically into engine

class RuleEngine(Process):

    def __init__(self, config):
        Process.__init__(self)
        self.name = 'RuleEngine'
        self.config = config
        self.database = DatabaseHandler(self.config.name)
        self.logutil = KBLogUtil(self.config.name, self.name)
        self.wids = WIDSClient(self.config.server_ip, self.config.server_port)
        self.active = None
        self.rules = []

        #///dev///
        self.rules.append(RuleDissasocAttack())
        #////////

    def run(self):
        self.logutil.log('Starting Execution')        
        self.active = True
        self.start_time = dateToMicro(datetime.utcnow())

        while self.active:
    
            if DEV_DEBUG:
                self.logutil.debug('Checking for new rules')
                time.sleep(3)

            # check server for new rules: 'GET /rules/updatecheck', if so load new rules
            '''
            if self.wids.checkNewRules():
                new_rules = self.wids.getNewRules()
            '''

            # evaluate each rule serially
            self.logutil.debug('Evaluating rules')
            for RuleObject in self.rules:
                self.evaluateRule(RuleObject)

        self.logutil.log('Terminating Execution')


    # TODO - replace the internal database with a REST call to query database for events
    def evaluateRule(self, RuleObject):
        self.logutil.dev('Evaluating Rule: {0} (EventIndex: {1})'.format(RuleObject.name, RuleObject.event_index))
        for condition in RuleObject.event_conditions:
            module = condition[0]
            event  = condition[1]
            count  = condition[2]

            # TODO - replace this direct database query with REST call ????
            query = self.database.session.query(Event).filter(Event.module == module).filter(Event.name == event).filter(Event.datetime > self.start_time).filter(Event.id > RuleObject.event_index)

            results_count = query.limit(count).count()
            self.logutil.dev('Event: {0} - Found: {1} (Events Needed: {2})'.format(event, results_count, count))
            if not results_count >= count:
                return False
            last_result = query.order_by(Event.id.desc()).limit(count).first()
            RuleObject.event_index = last_result.id
            self.logutil.log('>>> Rule Conditions Met ({0})'.format(RuleObject.name))
            for action in RuleObject.execute_actions:
                actionType   = action[0]
                actionParams = action[1]
                if actionType == 'GenerateAlert':
                    self.action_GenerateAlert(RuleObject.name,  actionParams)
                if actionType == 'GenerateLog':
                    self.action_GenerateLog(RuleObject.name, actionParams)
    
            
    def action_GenerateLog(self, rule_name, action_parameters):
        self.logutil.log('Execution GenerateLog Action for Rule {0}'.format(rule_name))
        pass

    def action_GenerateAlert(self, rule_name, action_parameters):
        self.logutil.log('Executing GenerateAlert Action for Rule {0}'.format(rule_name))
        self.wids.generateAlert(rule_name)

    def shutdown(self):
        self.active = False
        self.terminate()

