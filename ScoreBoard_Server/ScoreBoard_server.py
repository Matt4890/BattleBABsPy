'''
Desc.
'''

''''''#
''''''# Imports
''''''#

import socket
import os

''''''#
''''''# Functions
''''''#

def getDataFilePath():
	scriptDir	= os.path.dirname(__file__)
	dataFile	= "data/teamscore.txt"
	path		= os.path.join(scriptDir, dataFile)
	return path

def readTeamScores():
	fileHandle	= open(getDataFilePath(), "r")
	dataLines	= fileHandle.readlines()
	fileHandle.close()
	return dataLines

def saveTeamScores():
	fileHandle	= open(getDataFilePath(), "w")

	dataLines = ""
	for team in scoreDict:
		dataLines += (team + ":" + str(scoreDict[team]) + "\r\n")

	fileHandle.writelines(dataLines)
	fileHandle.close()

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

for line in readTeamScores():
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

	for data in cookedData.split(","):
		team, score = data.split(":")
		scoreDict[team] += int(score)
		print("Team '%s' given %s point(s), now has %s point(s)." % (team, score, scoreDict[team]))

	saveTeamScores()