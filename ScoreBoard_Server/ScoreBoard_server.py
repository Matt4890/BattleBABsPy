'''
Desc.
'''

''''''#
''''''# Imports
''''''#

import socket

''''''#
''''''# Networking
''''''#

UDP_IP		= "127.0.0.1"
UDP_PORT	= 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

''''''#
''''''# Battle BAB Data
''''''#

scoreDict = {}

dataFile	= "data/teamscore.txt"
fileHandle	= open(dataFile, "r")
dataLines	= fileHandle.readLines()
fileHandle.close()

for line in dataLines:
	team, score = line.split(":")
	if team not in scoreDict:
		scoreDict[team] = int(score)

''''''#
''''''# Server Loop
''''''#

while True:

	rawData, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
	cookedData = rawData.decode("ascii").strip()

	print("\nReceived message:", cookedData)
	team, score = cookedData.split(":")

	scoreDict[team] += int(score)
	print("Team %s given %s point(s), now has %s points." % (team, score, scoreDict[team]))