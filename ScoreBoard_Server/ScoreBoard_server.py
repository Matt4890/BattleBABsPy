"""
Desc.
"""

''''''#*****************************************************************************************************
''''''# Imports
''''''#*****************************************************************************************************

import os
from os import listdir
from os.path import isfile, join
import pygame
import random
import socket
from threading import Thread
import time

''''''#*****************************************************************************************************
''''''# Thread Classes
''''''#*****************************************************************************************************

"""
Class ServerThread
SUMMARY: This class is setup as a thread for handling client events
INIT PARAMETERS:
	NONE
"""
class ServerThread(Thread):

	def __init__(self):
		Thread.__init__(self) # init threading
	"""
	run(self)
	SUMMARY: Main execution point of the class
	PARAMETERS:
		NONE
	RETURNS VOID
	"""
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
			print("\n\nReceived message: '%s' from" % cookedData, client)

			# If a client requested the next match...
			if cookedData == "NEXT_MATCH":
				print("Sending next match data to:", client)
				match	= getNextMatch()
				names = match.split(":")
				SOCK.sendto(match.encode("ascii"), client)
				setMatchQueued(names)
				print("Done.\n\n")
				continue

			# If a client requested for the scores to be reset...
			elif cookedData == "RESET_SCORES":
				resetScores()
				continue

			# If a client requested the matches to be reset...
			elif cookedData == "RESET_MATCHES":
				resetMatches()
				continue

			# If a client requested a full stat reset...
			elif cookedData == "RESET":
				resetScores()
				resetMatches()
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
					print("Team(s) not recognized. Ignoring.\n\n")

				continue

			# Otherwise... We can't comply to instructions we can't understand ¯\_(ツ)_/¯
			print("Message not recognized. Ignoring.\n\n")


''''''#*****************************************************************************************************
''''''# Generic Classes
''''''#*****************************************************************************************************

"""
Class Team
SUMMARY: This class defines a team
INIT PARAMETERS:
	string name - String of the team's name
	int score - integer of team's score
	int matchesPlayed - integer of matches played by team
	int matchesWon - integer of matches won by team
"""
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

	"""
	updateBalancedScore(self)
	SUMMARY: Updates the balanced (Overall Average) score of the team
	PARAMETERS:
		NONE
	RETURNS VOID
	"""
	def updateBalancedScore(self):
		self.balancedScore	= self.score // self.matchesPlayed if self.matchesPlayed > 0 else 0

	"""
	addMatch(self, score, won)
	SUMMARY: Adds match data to the team
	PARAMETERS:
		int score - integer score from the match
		bool won - Boolean for if this team won the match
	RETURNS VOID
	"""
	def addMatch(self, score, won):
		self.score			+= score
		self.matchesPlayed	+= 1
		self.matchesWon		+= 1 if won else 0
		self.updateBalancedScore()


"""
Class MatchSystem
SUMMARY: This class creates a queue framework for use with scoreboards
INIT PARAMETERS:
	int queued - integer of queued matches (defaults to 0 because why would you say there are already matches queued on creation?)
	int maxq - integer of maximum allowable queued matched (Have this match the number of unique scoreboard instances)
"""

class MatchSystem():
	def __init__(self, queued = 0, maxq = 2):
		self.queued	= queued
		self.maxq = maxq
		

	def __repr__(self):
		return "%s:%i" % (
			self.queued,
			self.maxq
		)

	"""
	setMax(self, value)
	SUMMARY: Sets the maximum number of queued matches
	PARAMETERS:
		int value - integer of maximum queued matches to have
	RETURNS VOID
	"""
	def setMax(self, value):
		self.maxq = value
	
	"""
	getMax(self)
	SUMMARY: Gets the current maximum number of queued matches
	PARAMETERS:
		NONE
	RETURNS: int maxq - integer of maximum number of queued matches
	"""
	def getMax(self):
		return self.maxq
	
	"""
	adjustQueued(self, deltaValue)
	SUMMARY: Adjusts the current number of queued matches by the delta given
	PARAMETERS:
		int deltaValue - integer of how many matches and in what direction to change the queued list by
	RETURNS VOID
	"""
	def adjustQueued(self, deltaValue):
		self.queued += deltaValue
		if self.queued < 0:
			self.queued = 0
	
	"""
	getQueued(self)
	SUMMARY: Gets the current number of queued matches
	PARAMETERS:
		NONE
	RETURNS: int queued - integer of number of matches queued
	"""
	def getQueued(self):
		return self.queued
"""
Class Music System
SUMMARY: Creates a Music system to play .ogg files optimally sampled at 44.1kHz. Most music files can be easily changed to this using Audacity
INIT PARAMETERS:
	NONE
"""
class MusicSystem():
	def __init__(self):
		self.canUtilize = False
		self.volume = 100
		self.queue = []
		self.playing = -1

	def __repr__(self):
		print("foo")

	"""
	loadSong(self)
	SUMMARY: Loads .ogg filenames from the music folder into a queue array
	PARAMETERS:
		NONE
	RETURNS: Case Dependent:
		If .ogg files exist in the music directory -> Returns list queue - a list containing filenames of playable files
		If no .ogg files exist in the music directory -> Returns VOID
	"""
	def loadSongs(self):
		filePath = getMusicFilePath()
		onlyFiles = [f for f in listdir(filePath) if isfile(join(filePath, f))] # get only files in the music directory
		print("Loading song files into queue...\n\n\n")
		for songFile in onlyFiles:
			print(songFile)
			split = songFile.strip().upper().split(".") # get extension off of file name
			for splitResult in split:
				print(">>" + splitResult)
			if split[len(split) - 1] != "OGG": # look a last item (incase multiple dots in path) and check extension
				onlyFiles.remove(songFile)
				print("><Removed %s from queue as its extension is not ogg" % (songFile))

		if len(onlyFiles) == 0:
			print("<>No music in directory! pygame music mixer wont be utilized")
			self.canUtilize = False
		else:
			print("<>OGG files were found. pygame music mixer will be utilized")
			self.canUtilize = True
			pygame.mixer.init(frequency=44100) # ensure music sample is 44100Hz for nice playback
			return onlyFiles

	"""
	getCurrentSongName(self)
	SUMMARY: Gets the current song's name
	PARAMETERS:
		NONE
	RETURNS: Case Dependent:
		IF playing = -1 -> RETURNS "NONE"
		IF playing != -1 -> RETURNS string song - name of song currently playing
	"""
	def getCurrentSongName(self):
		song = None
		songSplit = []
		if self.playing == -1:
			song = "None"
			return song
		else:
			songSplit = self.queue[self.playing].strip().upper().split(".")
			return songSplit[0]

	"""
	createQueue(self, fileList)
	SUMMARY: creates a queue and shuffles it
	PARAMETERS:
		fileList - list of filenames to use in queue
	RETURNS: VOID
	"""
	def createQueue(self, fileList):
		if self.canUtilize == True:
			print("Creating a music Queue...")
			self.queue = fileList
			print("Queue length is %i" % (len(self.queue)))
			print("Randomizing queue...")
			random.shuffle(self.queue)
			SONG_END = pygame.USEREVENT + 1
			pygame.mixer.music.set_endevent(SONG_END) # setup an event system so we can change music
		else:
			print("!!Cant be executed! mixer isnt enabled because no files found in music directory\n")

	"""
	getCurrentSongIndex(self)
	SUMMARY: Gets the current index of the song that is playing (in terms of the shuffled queue)
	PARAMETERS:
		NONE
	RETURNS int index - integer of the index in the queue of the current song
	"""
	def getCurrentSongIndex(self):
		return self.playing
	
	"""
	getQueueLength(self)
	SUMMARY: Gets the length of the queue
	PARAMETERS:
		NONE
	RETURNS int length - integer of the length of the queue list
	"""
	def getQueueLength(self):
		return len(self.queue)
	
	"""
	getQueue(slef)
	SUMMARY: Gets the entire queue list
	PARAMETERS:
		NONE
	RETURNS list queue - list of the queue for the music instance
	"""
	def getQueue(self):
		return self.queue
	
	"""
	playNextSongByIndex(self, index)
	SUMMARY: Starts playing the next song, referenced by the given index number
	PARAMETERS:
		int index - integer index into the queue array to get the next song to play
	RETURNS VOID
	"""
	def playNextSongByIndex(self, index):
		if self.canUtilize == True:
			print("Selecting song from index %i" % (index))
			print("Selected is :" + self.queue[index] + "\n\n")
			pygame.mixer.music.load(getMusicFilePath() + "/" + self.queue[index])
			pygame.mixer.music.play(1)
			self.playing = index
		else:
			print("!!Cant play a song, mixer music isnt utilized\n")
	
	"""
	playNextSongByName(self, name)
	SUMMARY: Starts playing the next song, referenced by name instead of index number
	PARAMETERS:
		string name - string of the next song to play
	RETURNS VOID
	"""
	def playNextSongByName(self, name):
		if self.canUtilize == True:
			pygame.mixer.music.stop()
			pygame.mixer.music.load(getMusicFilePath() + "/" + name)
			pygame.mixer.music.play(1)
			print("Now playing song: %s (picked by RNG by name)\n\n" % (name))
			self.playing = queue.index(name)
		else:
			print("!!Cant play a song, mixer music isnt utilized\n")
	

''''''#*****************************************************************************************************
''''''# Functions
''''''#*****************************************************************************************************

"""
resetScores()
SUMMARY: Resets the scores of each team
PARAMETERS:
	NONE
RETURNS VOID
"""
def resetScores():
	print("Resetting team scores to 0...")
	for team in TEAM_DICT:
		TEAM_DICT[team].score = 0
		TEAM_DICT[team].updateBalancedScore()
	saveTeamData()
	print("Done.")

"""
resetMatches()
SUMMARY: Resets the matches played and won of each team, and generates a new match list
PARAMATERS:
	NONE
REUTNRS VOID
"""
def resetMatches():
	print("Generating a new match list...")
	genNewMatches(list(TEAM_DICT.keys()))
	print("Resetting team matches...")
	for team in TEAM_DICT:
		TEAM_DICT[team].matchesPlayed = 0
		TEAM_DICT[team].matchesWon = 0
		TEAM_DICT[team].updateBalancedScore()
	Queue.adjustQueued(-Queue.getQueued())
	print("Done.")
	updateLeaderboard()

"""
constructTeamFromStr(string)
SUMMARY: Constructs a Team instance from the given string
PARAMETERS:
	string string - string in format "Name:Score:Played:Won" to create a team from
RETURNS Team team - team class instance initialized based off of given string
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
"""
getDataFilePath()
SUMMARY: Gets the file path to the data folder for future reference
PARAMETERS:
	NONE
RETURNS: Case Dependent:
	IF path exists -> Returns data folder path
	IF path doesn't exist -> Returns VOID and raises FileNotFoundError
"""
def getDataFilePath():
	scriptDir	= os.path.dirname("__file__")
	dataFolder	= "data"
	path		= os.path.join(scriptDir, dataFolder)
	if(os.path.exists(path)):
		return path
	else:
		raise FileNotFoundError()

"""
getMusicFilePath()
SUMMARY: Gets the file path to the music folder for future reference. Similar to getDataFilePath()
PARAMETERS:
	NONE
RETURNS: Case Dependent:
	IF path exists -> Returns music folder path
	IF path doesn't exist -> Returns VOID and raises FileNotFoundError
"""
def getMusicFilePath():
	scriptDir	= os.path.dirname("__file__")
	dataFolder	= "music"
	path		= os.path.join(scriptDir, dataFolder)
	if(os.path.exists(path)):
		return path
	else:
		raise FileNotFoundError()

"""
Reads in the team object stored in './data/teams.txt'
"""
"""
readTeamData()
SUMMARY: Reads the team data in the teams data file
PARAMETERS:
	NONE
RETURNS: Case dependent
	IF teams file exists -> Returns dictionary of teams
	IF teams file doesn't exist -> Returns VOID and raises FileNotFoundError
"""
def readTeamData():
	if(os.path.exists(getDataFilePath() + "/teams.txt")):
		fileHandle	= open(getDataFilePath() + "/teams.txt", "r")
	else:
		raise FileNotFoundError("teams.txt data file cannot be found. Check naming and try again.")

	dataLines	= fileHandle.readlines()
	fileHandle.close()

	teamDict = {}
	for line in dataLines:
		cookedData = line.strip().upper()
		team = constructTeamFromStr(cookedData)
		teamDict[team.name] = team

	return teamDict

"""
saveTeamData()
SUMMARY: Saves the team data in the team dictionary to the teams data file
PARAMETERS:
	NONE
RETURNS VOID
"""
def saveTeamData():
	dataLines = []
	for team in TEAM_DICT:
		dataLines.append(repr(TEAM_DICT[team]) + "\n")

	#open line chooses to either make the file or write to it depending on if it exists
	if(os.path.exists(getDataFilePath() + "/teams.txt")):
		fileHandle = open(getDataFilePath() + "/teams.txt", "w")
	else:
		fileHandle = open(getDataFilePath() + "/teams.txt", "x")

	fileHandle.writelines(dataLines)
	fileHandle.flush() # sanity flush, shouldn't be needed but you never know
	fileHandle.close()

	updateLeaderboard()

"""
genNewMatches(teams)
SUMMARY: Generates a new matchlist from the given list of teams, round-robin style and shuffled into random order
PARAMETERS:
	list teams - list of team names to create matches with
RETURNS VOID
"""
def genNewMatches(teams):
	matches = []
	for i in range(0, len(teams) - 1):
		for j in range(i + 1, len(teams)):
			matches.append(teams[i] + ":" + teams[j] + "\n")
	random.shuffle(matches)

	if (os.path.exists(getDataFilePath() + "/matches.txt")):
		fileHandle	= open(getDataFilePath() + "/matches.txt", "w")
	else:
		fileHandle = open(getDataFilePath() + "/matches.txt", "x")

	fileHandle.writelines(matches)
	fileHandle.close()

"""
getMatchList()
SUMMARY: gets the current stored matchlist from the matches text file
PARAMETERS:
	NONE
RETURNS: Case Dependent:
	IF matches file exists -> Returns list of lines from the matches text file
	IF matches file doesn't exist -> Returns VOID and raises FileNotFoundError
"""
def getMatchList():
	if(os.path.exists(getDataFilePath() + "/matches.txt")):
		fileHandle	= open(getDataFilePath() + "/matches.txt", "r")
	else:
		raise FileNotFoundError("matches.txt could not be found in the data folder, check naming and try again.")
	dataLines	= fileHandle.readlines()
	fileHandle.close()

	dataLines = [line.strip() for line in dataLines]

	return dataLines

"""
Finds and returns the next match in the 'matches.txt' file.
A completed match is noted by a '~' as the first character of the line.

Returns : A string of the teams in the next match formatted as TEAM1:TEAM2.
"""
Queue = MatchSystem(0,2) # start queue system, initial queue of 0, max of 2

"""
getnextMatch()
SUMMARY: gets the next match that isn't already queued and returns it
PARAMETERS:
	NONE
RETURNS: Case Dependent:
	IF Matchlist is empty OR total number of queued matches is >= to maximum number of queued matches -> RETURNS string "NONE"
	IF Matchlist isn't empty AND total number of queued matches < maximum number of queued matched -> RETURNS string of next match
"""
def getNextMatch():
	match = ""
	matchList = getMatchList()
	if len(matchList) == 0:
		print("Matchlist is empty! Returning junk data so it isnt formatted")
		match = "NONE"
		return match
	else:
		if Queue.getQueued() >= Queue.getMax():
			print("Too many matches queued! returning junk data so it isnt formatted")
			match = "NONE"
			return match
		else:
			for line in getMatchList():
				if line[0] != "~":
					match = line.strip()
					if match.find(">") == -1:
						break
			match = "NONE" if match == "" else match
			print("selected match: %s" % (match))
			Queue.adjustQueued(1)
			print("queued is %i, max %i" % (Queue.getQueued(), Queue.getMax()))
			return match

"""
setMatchCompleted(match)
SUMMARY: Sets a match as "completed" in the matchlist file, meaning it deletes it from the file. Also decrements the total number of queued matches
PARAMETERS:
	string match - match string to delete
RETURNS VOID
"""
def setMatchCompleted(match):
	# Gotcha now, ya damn bug.
	if len(match) != 2 or not all(team in TEAM_DICT for team in match):
		return

	if(os.path.exists(getDataFilePath() + "/matches.txt")):
		fileHandle	= open(getDataFilePath() + "/matches.txt", "r")
	else:
		raise FileNotFoundError("matches.txt could not be found, double check naming and try again.")
	dataLines	= fileHandle.readlines()
	fileHandle.close()
	matchStr_0 = match[0] + ":" + match[1]
	matchStr_1 = match[1] + ":" + match[0]
	for i in range(len(dataLines)):
		if dataLines[i].strip().strip('>') == matchStr_0 or dataLines[i].strip() == matchStr_1:
			dataLines.pop(i)
			break

	if(os.path.exists(getDataFilePath() + "/matches.txt")):
		fileHandle	= open(getDataFilePath() + "/matches.txt", "w")
	else:
		fileHandle	= open(getDataFilePath() + "/matches.txt", "x")

	fileHandle.writelines(dataLines)
	fileHandle.close()
	Queue.adjustQueued(-1)

"""
setMatchQueued(match)
SUMMARY: Sets a match as queued in the matlist file and increments the number of queued matches. Similar to setMatchCompleted
PARAMETERS:
	string match - match string to set as queued
RETURNS VOID
"""
def setMatchQueued(match):
	# Gotcha now, ya damn bug.
	if len(match) != 2 or not all(team in TEAM_DICT for team in match):
		return

	if(os.path.exists(getDataFilePath() + "/matches.txt")):
		fileHandle	= open(getDataFilePath() + "/matches.txt", "r")
	else:
		raise FileNotFoundError("matches.txt could not be found, double check naming and try again.")
	dataLines	= fileHandle.readlines()
	fileHandle.close()

	matchStr_0 = match[0] + ":" + match[1]
	matchStr_1 = match[1] + ":" + match[0]
	for i in range(len(dataLines)):
		if dataLines[i].strip().strip('>') == matchStr_0 or dataLines[i].strip() == matchStr_1:
			dataLines[i] = ">" + dataLines[i]
			break

	if(os.path.exists(getDataFilePath() + "/matches.txt")):
		fileHandle	= open(getDataFilePath() + "/matches.txt", "w")
	else:
		fileHandle	= open(getDataFilePath() + "/matches.txt", "x")
		
	fileHandle.writelines(dataLines)
	fileHandle.close()

"""
updateLeaderboard
SUMMARY: Updates the team order on the leaderboard, from largest (1st) to smallest (last).
PARAMETERS:
	NONE
RETURNS VOID
"""
def updateLeaderboard():
	global LEADERBOARD
	LEADERBOARD = sorted(TEAM_DICT, key=lambda team: TEAM_DICT[team].score, reverse=True)
	print("\n\nLeaderboard updated. Current ranking:")
	for team in LEADERBOARD:
		print(TEAM_DICT[team].__repr__().replace(':', "\t\t", 1))
	print("\n\n")

"""
blitInRect(rect, font, colour, *strings, startingY=-1, gapY=0)
SUMMARY: Renders and blits a series of strings in the centre of a rect.
	If multiple strings are given, they are blitted in a column of descending order.
	The whole column of blitted text is still centred perfect in the rect.

PARAMETERS:
	rect		: The rect to draw the text into.
	font		: The font to render the text with.
	colour		: The colour to render the text in.
	*strings	: A series of strings the render and blit into the rect.
	startingY	: If overridden, this will be the y value the first string is centred on.
	gapY		: If overridden, this will be the gap between text elements (bottom to top)
RETURNS VOID
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

"""
blitColumn(rect, *rows)
SUMMARY: creates a blit column via blitInRect
PARAMETERS:
	rect - rectangle to draw the text of the column into
	*rows - series of strings to write into the rect
RETURNS VOID
"""
def blitColumn(rect, *rows):
	blitInRect(rect, MEDIUM_FONT, C_CYAN, *rows, startingY=yUnit//2, gapY=yUnit//4)

''''''#*****************************************************************************************************
''''''# Networking
''''''#*****************************************************************************************************

UDP_IP		= "0.0.0.0" # This IP is the UDP Anything IP, so we can receive from al lthe scoreboards without actually knowing their individual IPs
UDP_PORT	= 5005 # Port to listen on, ensure it matches what is set on the scoreboard clients

SOCK = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
SOCK.bind((UDP_IP, UDP_PORT))

''''''#*****************************************************************************************************
''''''# Battle BAB Data
''''''#*****************************************************************************************************

TEAM_DICT = readTeamData()
LEADERBOARD = list(TEAM_DICT.keys())
updateLeaderboard()

''''''#*****************************************************************************************************
''''''# PyGame GUI Data
''''''#*****************************************************************************************************

# Init
pygame.init()

# Window Parameters
WINDOW_WIDTH	= 1920
WINDOW_HEIGHT	= 1080
xUnit			= WINDOW_WIDTH // 16 #Grid system X axis snaps
yUnit			= WINDOW_HEIGHT // 9 #Grid system Y axis snaps
DISPLAY_SURFACE	= pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))#, pygame.FULLSCREEN)# <-- uncomment for fullscreen application
pygame.display.set_caption("Battle BABs - Server")

# Fonts
LARGE_FONT	    = pygame.font.SysFont("monospace", 52, True)
MEDIUM_FONT	    = pygame.font.SysFont("monospace", 36, True)
SMALL_FONT	    = pygame.font.SysFont("monospace", 24, True)
SUPERSMALL_FONT	= pygame.font.SysFont("monospace", 18, True)

# Colours   R    G    B
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

''''''#*****************************************************************************************************
''''''# Run!
''''''#*****************************************************************************************************

# Start the game logic controller
GameController = ServerThread() # Create an instance of the ServerThread class
GameController.daemon = True # Make the threaded instance a daemon thread so that it will exit when the main program exits
GameController.start() # Start the Server thread

MusicDJ = MusicSystem() # Create a "DJ" for music control
songs = MusicDJ.loadSongs()
MusicDJ.createQueue(songs)
MusicDJ.playNextSongByIndex(0)

# Start the GUI controller
pygame.draw.rect(DISPLAY_SURFACE, *R_TITLE_C)
blitInRect(R_TITLE_C[1], LARGE_FONT, C_MINT, "Battle", "BABs", time.strftime("%Y"))

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

''''''#*****************************************************************************************************
''''''# MAIN CLIENT LOOP
''''''#*****************************************************************************************************


while True:

	# You shouldn't need to sort the leaderboard here... but it prints out of order if you don't?
	# Apparently lists don't keep their order outside of a function?
	# Or it thinks its a local variable in the function?
	#LEADERBOARD = sorted(TEAM_DICT, key=lambda team: TEAM_DICT[team].score, reverse=True)
	pygame.draw.rect(DISPLAY_SURFACE, *R_CONTROL_C)
	blitInRect(R_CONTROL_C[1], SUPERSMALL_FONT, C_DGRAY, "Current Song:", MusicDJ.getCurrentSongName())

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
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			print("Quitting...")
			quit()
		elif event.type == (pygame.USEREVENT + 1): #Music ended
			queue = MusicDJ.getQueue() # we need the queue so we can choose a random song
			next_song = random.choice(queue) # choose a random song from the queue
			while next_song == queue[MusicDJ.getCurrentSongIndex()]: #anti-repeat loop
				next_song = random.choice(queue)
			MusicDJ.playNextSongByName(next_song) # load the next song and play it	
	pygame.display.update() # update the display
	time.sleep(0.02) # CPU usage limiting delay, 20ms