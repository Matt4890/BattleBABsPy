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

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

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
	if '1' in ser.readline().decode("ascii"):
		sock.sendto(b'1:1', (UDP_IP, UDP_PORT))
	#sock.sendto(ser.readline(), (UDP_IP, UDP_PORT))

for line in sys.stdin:
	if ',' in line:
		for msg in line.split(','):
			sock.sendto(msg.encode('ascii'), (UDP_IP, UDP_PORT))
	else:
		sock.sendto(line.encode('ascii'), (UDP_IP, UDP_PORT))