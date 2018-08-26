"""
Desc.
"""

''''''#
''''''# Imports
''''''#

import os
import pygame
import random
import socket
from threading import Thread

''''''#
''''''# Thread Classes
''''''#

class ServerThread(Thread):

	def __init__(self):
		Thread.__init__(self)

	def run(self):
		"""
		Waits until a UDP message is received.

		Tries to match the message to a command.
		If no message is found, it will see if the message could be formatted in a scoring message.
		A score message must be formatted as TEAM:SCORE_DELTA, which you can chain together with ','.
		After modifying points, the match will be marked as 'completed' in the 'matches.txt' file (if it exists in the file).
		"""
		while True:

			# Wait for and gather data to be used.
			rawData, client = SOCK.recvfrom(1024) # buffer size is 1024 bytes
			cookedData = rawData.decode("ascii").strip().upper()
			print("\nReceived message: '%s' from" % cookedData, client)

			# If a client requested the next match...
			if cookedData == "NEXT_MATCH":
				print("Sending next match data to:", client)
				match	= getNextMatch()
				SOCK.sendto(match.encode("ascii"), client)
				print("Done.")
				continue

			# If a client requested for the scores to be reset...
			if cookedData == "RESET_SCORES":
				print("Resetting team scores to 0...")
				for key in SCORE_DICT:
					SCORE_DICT[key] = 0
				saveTeamScores()
				print("Done.")
				continue

			# If a client requested the matches to be reset...
			if cookedData == "RESET_MATCHES":
				print("Generating a new match list...")
				genNewMatches(list(SCORE_DICT.keys()))
				print("Done.")
				continue

			# If the message has the potential to be formatted as a scoring message...
			if cookedData.count(":") == cookedData.count(",") + 1:
				msgs	= cookedData.split(",")
				match	= []
				scores	= []

				# Fracture data for easy world domination... I mean for easy "manipulation"... Mostly to check the teams are real first.
				for msg in msgs:
					team, score = msg.split(":")
					team, score = team.upper(), int(score)
					match.append(team)
					scores.append(score)

				# Check that all of the teams referenced actually exist before modifying scores.
				if all(team in SCORE_DICT for team in match):
					for i in range(0, len(match)):
						SCORE_DICT[match[i]] += scores[i]
						print("Team '%s' given %i point(s), now has %i point(s)." % (match[i], scores[i], SCORE_DICT[match[i]]))
					setMatchCompleted(match)
					saveTeamScores()
				else:
					print("Team(s) not recognized. Ignoring.")

				continue

			# Otherwise... We can't comply to instructions we can't understand ¯\_(ツ)_/¯
			print("Message not recognized. Ignoring.")

class GUIThread(Thread):

	def __init__(self):
		Thread.__init__(self)

	def run(self):
		"""
		Does a thing.
		"""
		while True:

			# Update some variables
			width, height = DISPLAY_SURFACE.get_size()

			# Background
			DISPLAY_SURFACE.fill((56, 72, 88))

			# Title Bar

			# Leaderboard

			# Match List

			# Buttons

			# Display Updates
			pygame.display.update()


''''''#
''''''# Generic Classes
''''''#

class Team():

	def __init__(self, name = "I need a name, dumbass", score = 0, matchesPlayed = 0, matchesWon = 0):
		self.name			= name.upper()
		self.score			= score
		self.matchesPlayed	= matchesPlayed
		self.matchesWon		= matchesWon

	def genDataStr(self):
		return "%s:%i:%i:%i" % (
			self.name,
			self.score,
			self.matchesPlayed,
			self.matchesWon
		)

''''''#
''''''# Functions
''''''#

"""
'NAME:SCORE:MATCHES_PLAYED:MATCHES_WON'
"""
def createTeamFromStr(string):
	rawBits = string.split(":")
	cookedBits = []
	try:
		cookedBits = [str(bit).upper() if bit is rawBits[0] else int(bit) for bit in rawBits]
	except Exception as e:
		raise ValueError("Cannot format string into team. Must be formatted 'NAME:SCORE:MATCHES_PLAYED:MATCHES_WON'.")
		print("OwO what's this?")
		raise e
		print("A weird script, that's what.")
		print("If you see this, some shit is reallllly fucked up.")
	return Team(*bits)

"""
Finds the absolute file path to the script's local data directory.

Returns : The path to the data folder.
"""
def getDataFilePath():
	scriptDir	= os.path.dirname("__file__")
	dataFolder	= "data"
	path		= os.path.join(scriptDir, dataFolder)
	return path

"""
Reads in the team object stored in './data/teams.txt'
"""
def readTeamData():
	fileHandle	= open(getDataFilePath() + "/teams.txt", "r")
	dataLines	= fileHandle.readlines()
	fileHandle.close()

	scoreDict = {}
	for line in dataLines:
		teamName, score = line.split(":")
		teamName, score = teamName.upper(), int(score)
		if teamName not in scoreDict:
			scoreDict[teamName] = score

	return scoreDict

"""
Saves the data stored in the score dictionary into the 'teamscore.txt' file in the data directory.
Each line is formatted as: TEAM:SCORE.
"""
def saveTeamScores():
	fileHandle	= open(getDataFilePath() + "/teamscore.txt", "w")

	dataLines = []
	for team in SCORE_DICT:
		dataLines.append(team + ":" + str(SCORE_DICT[team]) + "\r\n")

	fileHandle.writelines(dataLines)
	fileHandle.close()
	
	updateLeaderboard()

"""
Takes a list of teams, and creates a round-robin style match list where each team faces every other team once.
The match list is then shuffled into a random order and written to data/matches.txt.
Each line is formatted as: TEAM1:TEAM2.
rRR
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
A completed match is noted by a '~' as the first character of the line.

Returns : A string of the teams in the next match formatted as TEAM1:TEAM2.
"""
def getNextMatch():
	fileHandle	= open(getDataFilePath() + "/matches.txt", "r")
	dataLines	= fileHandle.readlines()
	fileHandle.close()

	match = ""
	for line in dataLines:
		if line[0] != "~":
			match = line.strip()
			break
	match = "NONE" if match == "" else match
	
	return match

"""
Sets a match in the 'matches.txt' file to 'completed' status.
A completed match is noted by a '~' as the first character of the line.

match : A list of teams in the completed match.
"""
def setMatchCompleted(match):
	# Gotcha now, ya damn bug.
	if len(match) != 2 or not all(team in SCORE_DICT for team in match):
		return

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

"""
Updates the global LEADERBOARD list.
It is sorted by each team's score, largest to smallest.
"""
def updateLeaderboard():
	LEADERBOARD = sorted(SCORE_DICT, key=SCORE_DICT.__getitem__, reverse=True)
	print("Leaderboard updated. Current ranking:")
	for team in LEADERBOARD:
		print(team, "\t\t", SCORE_DICT[team])

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
LEADERBOARD = list(SCORE_DICT.keys())
updateLeaderboard()

''''''#
''''''# PyGame GUI Data
''''''#

pygame.init()

WINDOW_WIDTH	= 1920
WINDOW_HEIGHT	= 1080
DISPLAY_SURFACE	= pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))#, pygame.FULLSCREEN) <-- Use for fullscreen
pygame.display.set_caption("Battle BABs - Server")

MAIN_FONT	= pygame.font.SysFont("monospace", 32, True)
SMALL_FONT	= pygame.font.SysFont("monospace", 16, True)

''''''#
''''''# Run!
''''''#

# Start the game logic controller
GameController = ServerThread()
GameController.start()

# Start the GUI controller
GUIController = GUIThread()
GUIController.start()