"""
Desc.
"""

''''''#
''''''# Imports
''''''#

import random
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

def genNewMatches(teams):
	matches = []
	for i in range(0, len(teams) - 1):
		for j in range(i + 1, len(teams)):
			matches += (teams[i] + ":" + teams[j] + "\r\n")

	fileHandle	= open(getDataFilePath() + "/matches.txt", "w")
	fileHandle.writelines(matches)
	fileHandle.close()

def getNextMatch():
	fileHandle	= open(getDataFilePath() + "/matches.txt", "r")
	dataLines	= fileHandle.readlines()
	fileHandle.close()

	match = ""
	for line in dataLines:
		if line[0] != "~":
			match = line
			break
	
	return match

def setMatchCompleted(match):
	fileHandle	= open(getDataFilePath() + "/matches.txt", "r")
	dataLines	= fileHandle.readlines()
	fileHandle.close()

	matchStr = match[0] + ":" + match[1]
	for line in dataLines:
		if line == matchStr:
			line = "~" + matchStr
			break

	fileHandle	= open(getDataFilePath() + "/matches.txt", "w")
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