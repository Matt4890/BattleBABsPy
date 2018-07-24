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

"""
Finds the absolute file path to the script's local data directory.

Returns : The path to the data folder.
"""
def getDataFilePath():
	scriptDir	= os.path.dirname(__file__)
	dataFolder	= "data"
	path		= os.path.join(scriptDir, dataFolder)
	return path

"""
Reads the data stored in the 'teamscore.txt' file in the data directory.
Each line is formatted as: TEAM:SCORE

Returns : A dictionary of teams and their appropriate scores.
"""
def readTeamScores():
	fileHandle	= open(getDataFilePath() + "/teamscore.txt", "r")
	dataLines	= fileHandle.readlines()
	fileHandle.close()

	scoreDict = {}
	for line in dataLines:
		team, score = line.split(":")
		team, score = team.upper(), int(score)
		if team not in scoreDict:
			scoreDict[team] = score

	return scoreDict

"""
Saves the data stored in the score dictionary into the 'teamscore.txt' file in the data directory.
Each line is formatted as: TEAM:SCORE
"""
def saveTeamScores():
	fileHandle	= open(getDataFilePath() + "/teamscore.txt", "w")

	dataLines = ""
	for team in SCORE_DICT:
		dataLines += (team + ":" + str(SCORE_DICT[team]) + "\r\n")

	fileHandle.writelines(dataLines)
	fileHandle.close()

"""
Takes a list of teams, and creates a round-robin style match list where each team faces every other team once.
The match list is then shuffled into a random order and written to data/matches.txt.
Each line is formatted as: TEAM1:TEAM2

teams : A list of team names as strings.
"""
def genNewMatches(teams):
	matches = []
	for i in range(0, len(teams) - 1):
		for j in range(i + 1, len(teams)):
			matches.append(teams[i] + ":" + teams[j] + "\r\n")
	random.shuffle(matches)

	fileHandle	= open(getDataFilePath() + "/matches.txt", "w")
	fileHandle.writelines(matches)
	fileHandle.close()

"""
Finds and returns the next match in the 'matches.txt' file.

Returns : A string of the teams in the next match formatted as TEAM1:TEAM2.
"""
def getNextMatch():
	fileHandle	= open(getDataFilePath() + "/matches.txt", "r")
	dataLines	= fileHandle.readlines()
	fileHandle.close()

	match = []
	for line in dataLines:
		if line[0] != "~":
			match = line
			break
	
	return match

"""
Sets a match in the 'matches.txt' file to 'completed' status.
A completed match is noted by a '~' as the first character of the line.

match : A list of teams in the completed match.
"""
def setMatchCompleted(match):
	fileHandle	= open(getDataFilePath() + "/matches.txt", "r")
	dataLines	= fileHandle.readlines()
	fileHandle.close()

	matchStr_0 = match[0] + ":" + match[1]
	matchStr_1 = match[1] + ":" + match[0]
	for i in range(len(dataLines)):
		if dataLines[i].strip() == matchStr_0 or dataLines[i].strip() == matchStr_1:
			dataLines[i] = "~" + dataLines[i]
			break

	fileHandle	= open(getDataFilePath() + "/matches.txt", "w")
	fileHandle.writelines(dataLines)
	fileHandle.close()

''''''#
''''''# Networking
''''''#

UDP_IP		= "127.0.0.1"
UDP_PORT	= 5005

SOCK = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
SOCK.bind((UDP_IP, UDP_PORT))

''''''#
''''''# Battle BAB Data
''''''#

SCORE_DICT = readTeamScores()

''''''#
''''''# Server Loop
''''''#

"""
Waits until a UDP message is received.
A message must be formatted as TEAM:SCORE_DELTA which you can chain together with ','
After modifying points, the match will be marked as 'completed' in the 'matches.txt' file (if it exists in the file)
"""
while True:

	rawData, addr = SOCK.recvfrom(1024) # buffer size is 1024 bytes
	cookedData = rawData.decode("ascii").strip()
	print("\nReceived message:", cookedData)

	if cookedData == "NEXT_MATCH":
		print(addr)
		SOCK.sendto(getNextMatch().encode("ascii"), addr)
		continue

	msgs = cookedData.split(",")
	match = []
	for msg in msgs:
		team, score = msg.split(":")
		team, score = team.upper(), int(score)
		match += team
		SCORE_DICT[team] += score
		print("Team '%s' given %i point(s), now has %i point(s)." % (team, score, SCORE_DICT[team]))

	setMatchCompleted(match)
	saveTeamScores()