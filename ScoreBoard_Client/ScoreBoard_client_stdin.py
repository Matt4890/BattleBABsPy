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

UDP_IP = "255.255.255.255"
UDP_PORT = 5005

SOCK = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
SOCK.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST,1)

# List of commands that should expect a message back from the server
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
		rawData, addr = SOCK.recvfrom(1024) # 1kiB buffer size
		print(rawData.decode("ascii"))

''''''#
''''''# Client Loop
''''''#

for line in sys.stdin:
	for cmd in line.split('|'):
		sendCmd(cmd)
