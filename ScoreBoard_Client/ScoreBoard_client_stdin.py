'''
Desc.
'''

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

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

''''''#
''''''# Client Loop
''''''#

for line in sys.stdin:
	if ',' in line:
		for msg in line.split(','):
			sock.sendto(msg.encode('ascii'), (UDP_IP, UDP_PORT))
	else:
		sock.sendto(line.encode('ascii'), (UDP_IP, UDP_PORT))