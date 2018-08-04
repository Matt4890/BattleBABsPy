"""
Desc.
"""

''''''#
''''''# Imports
''''''#

import socket
import sys

''''''#
''''''# Networking
''''''#

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

SOCK = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

''''''#
''''''# Client Loop
''''''#

for line in sys.stdin:
	if '|' in line:
		for msg in line.split('|'):
			SOCK.sendto(msg.encode('ascii'), (UDP_IP, UDP_PORT))
	else:
		SOCK.sendto(line.encode('ascii'), (UDP_IP, UDP_PORT))
		if line.strip().upper() == "NEXT_MATCH":
			rawData, addr = SOCK.recvfrom(1024)
			print(rawData.decode("ascii"))