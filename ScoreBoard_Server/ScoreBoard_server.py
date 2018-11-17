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
import time

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
			elif cookedData == "RESET_SCORES":
				print("Resetting team scores to 0...")
				for team in TEAM_DICT:
					TEAM_DICT[team].score = 0
					TEAM_DICT[team].updateBalancedScore()
				saveTeamData()
				print("Done.")
				continue

			# If a client requested the matches to be reset...
			elif cookedData == "RESET_MATCHES":
				print("Generating a new match list...")
				genNewMatches(list(TEAM_DICT.keys()))
				print("Resetting team matches...")
				for team in TEAM_DICT:
					TEAM_DICT[team].matchesPlayed = 0
					TEAM_DICT[team].matchesWon = 0
					TEAM_DICT[team].updateBalancedScore()
				print("Done.")
				updateLeaderboard()
				continue

			# If a client requested a full stat reset...
			elif cookedData == "RESET":
				SOCK.sendto("RESET_MATCHES".encode('ascii'), (UDP_IP, UDP_PORT))
				SOCK.sendto("RESET_SCORES".encode('ascii'), (UDP_IP, UDP_PORT))
				continue

			# If the message has the potential to be formatted as a scoring message...
			elif cookedData.count(":") == cookedData.count(",") + 1:
				msgs	= cookedData.split(",")
				match	= []
				scores	= []

				# Fracture data for easy world domination... I mean for easy "manipulation"...
				# Mostly to check the teams are real first.
				for msg in msgs:
					team, score = msg.split(":")
					team, score = team.upper(), int(score)
					match.append(team)
					scores.append(score)

				# Check that all of the teams referenced actually exist before modifying scores.
				if all(team in TEAM_DICT for team in match):
					winningScore = max(scores)
					for i in range(0, len(match)):
						team = TEAM_DICT[match[i]]
						team.addMatch(scores[i], scores[i] == winningScore)
						print("Team '%s' given %i point(s), now has %i point(s)." % (match[i], scores[i], team.score))
					setMatchCompleted(match)
					saveTeamData()
				else:
					print("Team(s) not recognized. Ignoring.")

				continue

			# Otherwise... We can't comply to instructions we can't understand ¯\_(ツ)_/¯
			print("Message not recognized. Ignoring.")

class GUIThread(Thread):

	def __init__(self):
		Thread.__init__(self)

		# Title Column
		pygame.draw.rect(DISPLAY_SURFACE, *R_TITLE_C)
		blitInRect(R_TITLE_C[1], LARGE_FONT, C_MINT, "Battle", "BABs", time.strftime("%Y"))

		# Control Column (?)
		pygame.draw.rect(DISPLAY_SURFACE, *R_CONTROL_C)

		# Leaderboard
		pygame.draw.rect(DISPLAY_SURFACE, *R_LEADERBOARD_R)
		blitInRect(R_LEADERBOARD_R[1], LARGE_FONT, C_MINT, "Leaderboard")
		pygame.draw.rect(DISPLAY_SURFACE, *R_RANK_R)
		blitInRect(R_RANK_R[1], LARGE_FONT, C_MINT, '#')
		pygame.draw.rect(DISPLAY_SURFACE, *R_NAME_R)
		blitInRect(R_NAME_R[1], LARGE_FONT, C_MINT, "Team")
		pygame.draw.rect(DISPLAY_SURFACE, *R_SCORE_R)
		blitInRect(R_SCORE_R[1], LARGE_FONT, C_MINT, "Score")
		pygame.draw.rect(DISPLAY_SURFACE, *R_MPLAYED_R)
		blitInRect(R_MPLAYED_R[1], SMALL_FONT, C_MINT, "Matches", "Played")
		pygame.draw.rect(DISPLAY_SURFACE, *R_MWON_R)
		blitInRect(R_MWON_R[1], SMALL_FONT, C_MINT, "Matches", "Won")
		pygame.draw.rect(DISPLAY_SURFACE, *R_BSCORE_R)
		blitInRect(R_BSCORE_R[1], SMALL_FONT, C_MINT, "Balanced", "Score")

		# Match List
		pygame.draw.rect(DISPLAY_SURFACE, *R_MATCHES_R)
		blitInRect(R_MATCHES_R[1], LARGE_FONT, C_MINT, "Match List")

	def run(self):
		"""
		Does a thing.
		"""
		while True:

			# You shouldn't need to sort the leaderboard here... but it prints out of order if you don't?
			# Apparently lists don't keep their order outside of a function?
			# Or it thinks its a local variable in the function?
			#LEADERBOARD = sorted(TEAM_DICT, key=lambda team: TEAM_DICT[team].score, reverse=True)

			# Leaderboard
			pygame.draw.rect(DISPLAY_SURFACE, *R_RANK_C)
			blitColumn(R_RANK_C[1], *[i for i in range(1,len(LEADERBOARD) + 1 if len(LEADERBOARD) < 12 else 13)])

			pygame.draw.rect(DISPLAY_SURFACE, *R_NAME_C)
			blitColumn(R_NAME_C[1], *[team for team in LEADERBOARD])

			pygame.draw.rect(DISPLAY_SURFACE, *R_SCORE_C)
			blitColumn(R_SCORE_C[1], *[TEAM_DICT[team].score for team in LEADERBOARD])

			pygame.draw.rect(DISPLAY_SURFACE, *R_MPLAYED_C)
			blitColumn(R_MPLAYED_C[1], *[TEAM_DICT[team].matchesPlayed for team in LEADERBOARD])

			pygame.draw.rect(DISPLAY_SURFACE, *R_MWON_C)
			blitColumn(R_MWON_C[1], *[TEAM_DICT[team].matchesWon for team in LEADERBOARD])

			pygame.draw.rect(DISPLAY_SURFACE, *R_BSCORE_C)
			blitColumn(R_BSCORE_C[1], *[TEAM_DICT[team].balancedScore for team in LEADERBOARD])

			# Match List
			pygame.draw.rect(DISPLAY_SURFACE, *R_MATCHES_C)
			blitColumn(R_MATCHES_C[1], *[match if len(match) <= 21 else match[:7] + "..." + match[match.find(':'):match.find(':') + 8] + "..." for match in getMatchList()])

			# Display Updates
			pygame.display.update()
			time.sleep(1)

''''''#
''''''# Generic Classes
''''''#

class Team():

	def __init__(self, name, score = 0, matchesPlayed = 0, matchesWon = 0):
		self.name			= name.upper()
		self.score			= score
		self.matchesPlayed	= matchesPlayed
		self.matchesWon		= matchesWon
		self.updateBalancedScore()

	def __repr__(self):
		return "%s:%i:%i:%i:%i" % (
			self.name,
			self.score,
			self.matchesPlayed,
			self.matchesWon,
			self.balancedScore
		)

	def updateBalancedScore(self):
		self.balancedScore	= self.score // self.matchesPlayed if self.matchesPlayed > 0 else 0

	def addMatch(self, score, won):
		self.score			+= score
		self.matchesPlayed	+= 1
		self.matchesWon		+= 1 if won else 0
		self.updateBalancedScore()

''''''#
''''''# Functions
''''''#

"""
'NAME:SCORE:MATCHES_PLAYED:MATCHES_WON'
"""
def constructTeamFromStr(string):
	rawBits = string.split(":")
	cookedBits = []
	try:
		cookedBits = [rawBits[0].upper(), *[int(bit) for bit in rawBits[1:-1]]]
	except Exception as e:
		raise ValueError("Cannot format string into team. Must be formatted 'NAME:SCORE:MATCHES_PLAYED:MATCHES_WON'.")
		print("OwO what's this?")
		raise e
		print("A weird script, that's what.")
	return Team(*cookedBits)

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

	teamDict = {}
	for line in dataLines:
		cookedData = line.strip().upper()
		team = constructTeamFromStr(cookedData)
		teamDict[team.name] = team

	return teamDict

"""
Saves the data stored in the score dictionary into './data/teams.txt'.
Each line is formatted as: TEAM:SCORE.
"""
def saveTeamData():
	dataLines = []
	for team in TEAM_DICT:
		dataLines.append(repr(TEAM_DICT[team]) + "\r\n")

	fileHandle	= open(getDataFilePath() + "/teams.txt", "w")
	fileHandle.writelines(dataLines)
	fileHandle.close()

	updateLeaderboard()

"""
Takes a list of teams, and creates a round-robin style match list where each team faces every other team once.
The match list is then shuffled into a random order and written to data/matches.txt.
Each line is formatted as: TEAM1:TEAM2.

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

def getMatchList():
	fileHandle	= open(getDataFilePath() + "/matches.txt", "r")
	dataLines	= fileHandle.readlines()
	fileHandle.close()

	dataLines = [line.strip() for line in dataLines]

	return dataLines

"""
Finds and returns the next match in the 'matches.txt' file.
A completed match is noted by a '~' as the first character of the line.

Returns : A string of the teams in the next match formatted as TEAM1:TEAM2.
"""
def getNextMatch():
	match = ""
	for line in getMatchList():
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
	if len(match) != 2 or not all(team in TEAM_DICT for team in match):
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
	global LEADERBOARD
	LEADERBOARD = sorted(TEAM_DICT, key=lambda team: TEAM_DICT[team].score, reverse=True)
	print("Leaderboard updated. Current ranking:")
	for team in LEADERBOARD:
		print(TEAM_DICT[team].__repr__().replace(':', "\t\t", 1))

"""
Renders and blits a series of strings in the centre of a rect.
If multiple strings are given, they are blitted in a column of descending order.
The whole column of blitted text is still centred perfect in the rect.

rect		: The rect to draw the text into.
font		: The font to render the text with.
colour		: The colour to render the text in.
*strings	: A series of strings the render and blit into the rect.
startingY	: If overridden, this will be the y value the first string is centred on.
gapY		: If overridden, this will be the gap between text elements (bottom to top)
"""
def blitInRect(rect, font, colour, *strings, startingY=-1, gapY=0):
	elements = [font.render(str(string), True, colour) for string in strings]
	totalY = sum([element.get_rect().height for element in elements[:-1]])
	midX = rect.width // 2
	midY = (rect.height // 2) - (totalY // 2) if startingY < 0 else startingY
	for element in elements:
		elementRect = element.get_rect(center = (rect.x + midX, rect.y + midY))
		DISPLAY_SURFACE.blit(element, elementRect)
		midY += gapY + elementRect.height

def blitColumn(rect, *rows):
	blitInRect(rect, MEDIUM_FONT, C_CYAN, *rows, startingY=yUnit//2, gapY=yUnit//4)

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

TEAM_DICT = readTeamData()
LEADERBOARD = list(TEAM_DICT.keys())
updateLeaderboard()

''''''#
''''''# PyGame GUI Data
''''''#

# Init
pygame.init()

# Window Parameters
WINDOW_WIDTH	= 1920
WINDOW_HEIGHT	= 1080
xUnit			= WINDOW_WIDTH // 16
yUnit			= WINDOW_HEIGHT // 9
DISPLAY_SURFACE	= pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))#, pygame.FULLSCREEN) <-- Use for fullscreen
pygame.display.set_caption("Battle BABs - Server")

# Fonts
LARGE_FONT	= pygame.font.SysFont("monospace", 52, True)
MEDIUM_FONT	= pygame.font.SysFont("monospace", 36, True)
SMALL_FONT	= pygame.font.SysFont("monospace", 24, True)

# Colours
C_LGRAY	= ( 72,  96, 112)
C_MGRAY	= ( 48,  64,  80)
C_DGRAY	= ( 28,  36,  44)
C_GRAY1	= ( 52,  72,  88)
C_GRAY2	= ( 60,  80,  96)
C_CYAN	= ( 32, 196, 220)
C_MINT	= ( 32, 255, 196)

# Rects
R_TITLE_C		= (C_DGRAY,	pygame.Rect(xUnit * 0,  yUnit * 0,  xUnit * 2,  yUnit * 5 ))

R_CONTROL_C		= (C_CYAN,	pygame.Rect(xUnit * 0,  yUnit * 5,  xUnit * 2,  yUnit * 4 ))

R_LEADERBOARD_R	= (C_DGRAY,	pygame.Rect(xUnit * 2,  yUnit * 0,  xUnit * 10, yUnit * 1 ))

R_RANK_R		= (C_MGRAY,	pygame.Rect(xUnit * 2,  yUnit * 1,  xUnit * 1,  yUnit * 1 ))
R_RANK_C		= (C_GRAY1,	pygame.Rect(xUnit * 2,  yUnit * 2,  xUnit * 1,  yUnit * 7 ))

R_NAME_R		= (C_MGRAY,	pygame.Rect(xUnit * 3,  yUnit * 1,  xUnit * 3,  yUnit * 1 ))
R_NAME_C		= (C_GRAY2,	pygame.Rect(xUnit * 3,  yUnit * 2,  xUnit * 3,  yUnit * 7 ))

R_SCORE_R		= (C_MGRAY,	pygame.Rect(xUnit * 6,  yUnit * 1,  xUnit * 2,  yUnit * 1 ))
R_SCORE_C		= (C_GRAY1,	pygame.Rect(xUnit * 6,  yUnit * 2,  xUnit * 2,  yUnit * 7 ))

R_MPLAYED_R		= (C_MGRAY,	pygame.Rect(xUnit * 8,  yUnit * 1,  xUnit * 1,  yUnit * 1 ))
R_MPLAYED_C		= (C_GRAY2,	pygame.Rect(xUnit * 8,  yUnit * 2,  xUnit * 1,  yUnit * 7 ))

R_MWON_R		= (C_MGRAY,	pygame.Rect(xUnit * 9,  yUnit * 1,  xUnit * 1,  yUnit * 1 ))
R_MWON_C		= (C_GRAY1,	pygame.Rect(xUnit * 9,  yUnit * 2,  xUnit * 1,  yUnit * 7 ))

R_BSCORE_R		= (C_MGRAY,	pygame.Rect(xUnit * 10, yUnit * 1,  xUnit * 2,  yUnit * 1 ))
R_BSCORE_C		= (C_GRAY2,	pygame.Rect(xUnit * 10, yUnit * 2,  xUnit * 2,  yUnit * 7 ))

R_MATCHES_R		= (C_DGRAY,	pygame.Rect(xUnit * 12, yUnit * 0,  xUnit * 4,  yUnit * 1 ))
R_MATCHES_C		= (C_LGRAY,	pygame.Rect(xUnit * 12, yUnit * 1,  xUnit * 4,  yUnit * 8 ))

''''''#
''''''# Run!
''''''#

# Start the game logic controller
GameController = ServerThread()
GameController.start()

# Start the GUI controller
GUIController = GUIThread()
GUIController.start()
