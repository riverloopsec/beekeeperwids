#!/usr/bin/python

DATA_PATH='/opt/kbwids/'

try:
    from setuptools import setup
except ImportError:
    print("No setuptools found, attempting to use distutils instead.")
    from distutils.core import setup

# Check that /opt/kbwids/ exists and has the right permissions
#import os, stat
#if (not os.path.isdir(DATA_PATH)):
#    os.mkdir(DATA_PATH)
#    #TODO make this permissions cleaner - chown to the correct user probably
#    os.chmod(DATA_PATH, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)

# Do the install
setup(name='beekeeperwids',
      version='0.1',
      description='Wireless Intrusion Detection System for 802.15.4/ZigBee',
      author='TBD',
      author_email='javier@riverloopsecurity.com',
      url='http://www.riverloopsecurity.com',
      packages=['beekeeperwids',
                'beekeeperwids.drone', 'beekeeperwids.drone.plugins', 'beekeeperwids.drone.plugins.capture',
                'beekeeperwids.wids', 'beekeeperwids.wids.modules',
                'beekeeperwids.utils'],
      scripts=['cli/zbdrone', 'cli/zbwids'],
      # This is a *nix specific path and will need to provide for other options on different systems
      #data_files=[(DATA_PATH,['./beekeeperwids/wids/modules/modules.xml'])],
      # A version of KillerBee earlier than 2.5.0 may work, but has not been tested.
      install_requires=['flask', 'killerbee >= 2.5.0', 'scapy >= 2.2.0-dev'],
      # Consider using Markdown such as in https://coderwall.com/p/qawuyq
      long_description = open('README.txt').read(),
     )
