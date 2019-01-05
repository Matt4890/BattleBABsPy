"""
Desc.
"""

''''''#
''''''# Imports
''''''#

import serial
import serial.tools.list_ports
import socket
import sys
import time
import warnings

''''''#
''''''# Networking
''''''#



''''''#
''''''# Serial
''''''#

for port in serial.tools.list_ports.comports():
	print(port)
	time.sleep(.1)

arduinoPorts = [ port.device for port in serial.tools.list_ports.comports() ] #if 'Arduino' in port.description ]

if not arduinoPorts:
	raise IOError("No Arduino found")

if len(arduinoPorts) > 1:
	warnings.warn('Multiple Arduinos found - using the first')

ser = serial.Serial(arduinoPorts[0])

''''''#
''''''# Client Loop
''''''#

while True:
	time.sleep(1)
