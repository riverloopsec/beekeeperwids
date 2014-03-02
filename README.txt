killerbeewids
-------------

killerbeewids is a Wireless Intrusion Detection System (WIDS) for
IEEE 802.15.4 (and can be extended for upper layers such as ZigBee, 6loWPAN, etc).

It was developed by River Loop Security, LLC and released at Troopers14.
River Loop Security (riverloopsecurity.com) specailizes in security asssesments including
low-level embeeded systems, custom hardware, and specailized radio protocols.

Contributions and suggestions are welcome!

Configuration
--------------

Install the software on your drone. Then execute 'zbdrone -run'.

Install the software on your WIDS backend (if different than the drone computer).
Then execute 'zbwids -run'.

Logs will be written to the logging directory, which is defined by the KBWIDS_LOG_PATH 
enviroment variable, if set, and otherwise defaults to the temp directory of your system. 
The logs are named for the system component which is producing them.

