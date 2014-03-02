#!/usr/bin/python

import json


def printList(section, data, order=None):
	'''
	prints a dictionary of data as a 2-dimensional table and auto computes the spacing
	'''
	spacing = (max(list(len(str(s)) for s in data.keys()))+1)
	print('\n[+]{0}\n'.format(section))
	if not order == None:
		keys = data.keys()
	else:
		keys = order
	for key in order:
		print(str(key).ljust(spacing) + ': ' + str(data[key]))




def printTable(section, table_dict_list):
	#print('///print table///')
	print('[+] {0}'.format(section))
	
	
def printSeparator():
	print("="*100)


'''

-------------------------------------------------------------------------------------------------------------------

{
	'general' : {
			'name' : 'xxx'
			'daemon.pid' : 'xxx'
		    }

	'drones' : [
			{'index' : 0, 'name':'kbdrone.0', 'url':'http:', 'tasks':4, 'plugins':1, 'interfaces':0/2 }
		   ]

	'plugins': [
			{'pid':xxxx, 'name':xxxxx, 'events':xxxxx}
		   ]

	'tasks':  [
			{'index':0, 'plugin':xxxx, 'drone':xxxx, 'uuid':xxxxx}
	          ]
}


-------------------------------------------------------------------------------------------------------------------

[+] DAEMON

NAME     : xxxxx
DAEMON   : xxxxx
ENGINE   : xxxxx
SERVER   : http://127.0.0.1:8888
LOGFILE  : /home/dev/etc/kb/kbwids.0.log
PIDFILE  : /home/dev/etc/kb/kbwids.0.pid 
DATABASE : /home/dev/etc/kb/kbwids.0.db

================================================================

[+] DRONES

I    NAME        URL                      TASKS   PLUGINS   INTERFACES
-    ----        ---                      ----    -------   ----------
0    kbdrone.0   http://127.0.0.1:9999    4       1         1/1

================================================================

[+] PLUGINS

PID    NAME                     Events
----   ----                     ------
XXXX   Bandwidth-1              xxx

=================================================================

[+] TASKS

I  PLUGIN               DRONE           UUID                   
-  ------               ------          ----
0  Bandwidth-1          kbdrone.0       1111-2222-3333-4444     














-------------------------------------------------------------------------------------------------------------------

KILLERBEE DRONE


PID   CHANNEL	PROCESS	  INTERFACE	TASK UUID	   CALLBACK

12324  11   CapturePlugin             /dev/ttyUSB0   245-28095-25480    
12443  11   CapturePlugin.Sniffer     /dev/ttyUSB0   
33134  11   CapturePlugin.Filter      /dev/ttyUSB0












'''







