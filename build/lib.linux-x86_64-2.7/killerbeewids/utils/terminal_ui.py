#!/usr/bin/python

import json


def printList(section, data, order=None):
	'''
	prints a dictionary of data as a 2-dimensional table and auto computes the spacing
	'''
	spacing = (max(list(len(str(s)) for s in data.keys()))+1)
	print('\n' + '='*70)
	print('\n[+] {0}\n'.format(section))
	if not order == None:
		keys = data.keys()
	else:
		keys = order
	for key in order:
		print(str(key).ljust(spacing) + ': ' + str(data[key]))




def printTable(section, data, order=None):

	print('\n' + '='*70)
	print('\n[+] {0}\n'.format(section))
	if len(data) == 0:
		return

	headers = {}
	for key in data[0].keys():
		v_max = len(max(list(str(d[key]) for d in data)))
		k_max = max(list(len(str(s)) for s in data[0].keys()))
		headers[key] = max([v_max,k_max]) + 3
	s1 = ''
	s2 = ''
	
	for key,spacing in headers.items():
		s1 += str(key).ljust(spacing)
		s2 += str('-'*len(str(key))).ljust(spacing)
	print(s1)
	print(s2)
	for line in data:
		s = ''
		for key,spacing in headers.items():
			s += str(line[key]).ljust(spacing)
		print(s)





	
	
	
def printSeparator():
	print("="*100)


'''
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







