"""
This is a terminal-based client for BattleBABs.
It runs in a terminal, sending commands to the server that are input via stdin.
Commands may be strung together in one line using the pipe '|' character.

Author: Matthew Allwright
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

recievingCmds = ["NEXT_MATCH"]

''''''#
''''''# Functions
''''''#

"""
Sends a command to the global socket.

cmd:	A string command.
"""
def sendCmd(cmd):

	# Send the command
	SOCK.sendto(cmd.encode('ascii'), (UDP_IP, UDP_PORT))

	# Recieve data back from the server if applicable
	if cmd.strip().upper() in recievingCmds:
		rawData, addr = SOCK.recvfrom(1024)
		print(rawData.decode("ascii"))

''''''#
''''''# Client Loop
''''''#

for line in sys.stdin:
	line = line.split('|')
	for cmd in line:
		sendCmd(cmd)
