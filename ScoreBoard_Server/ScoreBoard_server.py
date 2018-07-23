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
	dataFolder	= "data"
	path		= os.path.join(scriptDir, dataFolder)
	return path

def readTeamScores():
	fileHandle	= open(getDataFilePath() + "/teamscore.txt", "r")
	dataLines	= fileHandle.readlines()
	fileHandle.close()
	return dataLines

def saveTeamScores():
	fileHandle	= open(getDataFilePath() + "/teamscore.txt", "w")

	dataLines = ""
	for team in scoreDict:
		dataLines += (team + ":" + str(scoreDict[team]) + "\r\n")

	fileHandle.writelines(dataLines)
	fileHandle.close()

def genMatches(teams):
	# foo

def getNextMatch():
	fileHandle	= open(getDataFilePath() + "/matches.txt", "r")
	dataLines	= fileHandle.readlines()
	fileHandle.close()

	match = ""
	for line in dataLines:
		if line[0] not "~":
			match = line
			break
	
	return match

def setMatchCompleted(match):
	# foo

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
	team, score = team.upper(), int(score)
	if team not in scoreDict:
		scoreDict[team] = score

''''''#
''''''# Server Loop
''''''#

while True:

	rawData, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
	cookedData = rawData.decode("ascii").strip()
	print("\nReceived message:", cookedData)

	msgs = cookedData.split(",")
	match = []
	for msg in msgs:
		team, score = msg.split(":")
		team, score = team.upper(), int(score)
		match += team
		scoreDict[team] += score
		print("Team '%s' given %i point(s), now has %i point(s)." % (team, score, scoreDict[team]))

	saveTeamScores()