"""
GUI Client Program  with console backend for BattleBabs at Robert Thirsk High School.
Communicates with an arduino controller for score and match control (SERIAL) and a leaderboard server for
leaderboard statistics (UDP)


Author: Matthew Allwright
Modified By: Joshua Rasmussen
"""

''''''#*****************************************************************************************************
''''''# ---[ Imports ]---
''''''#*****************************************************************************************************

import os
import socket
import serial
import serial.tools.list_ports
import sys
import pygame
import time
import warnings
import threading

''''''#*****************************************************************************************************
''''''# ---[ Networking ]---
''''''#*****************************************************************************************************

UDP_IP = "255.255.255.255" #IP is UDP Broadcast IP
UDP_PORT = 5005 # use a port we *think* nothing is using...hopefully

SOCK = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # create a socket configured for UDP Datagram communication
SOCK.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST,1) # setup the socket to use UDP broadcast

# List of commands that should expect a message back from the server
recievingCmds = ["NEXT_MATCH"]



''''''#*****************************************************************************************************
''''''# ---[ CLASSES ]---
''''''#*****************************************************************************************************

"""
Class MatchFramework
SUMMARY: Provides the base framework for match management
INIT PARAMETERS:
	team1 - String of Team 1's name
	team2 - String of Team 2's name
	startTime - initial match length
"""
class MatchFramework():
	def __init__(self, team1 = "Team 1", team2 = "Team 2", startTime = 20):
		self.team1 = team1.upper() # Uppercase in case we get lowercases
		self.team2 = team2.upper() # Uppercase in case lowercases are received
		self.score1 = 0
		self.score2 = 0
		self.timeL = startTime
	
	def __repr__(self):
		return "%s:%i:%s:%i:%i" % (
			self.team1, 
			self.score1, 
			self.team2, 
			self.score2, 
			self.timeL
		)

	"""
	insertTeamNames(self, team1Name, team2Name)
	SUMMARY: Sets the names of the current teams
	PARAMETERS:
		team1Name - String of team 1's Name
		team2Name - String of team 2's Name
	RETURNS VOID
	"""
	def insertTeamNames(self, team1Name, team2Name):
		self.team1 = team1Name
		self.team2 = team2Name
		print("Set team 1 name to [%s] and team 2 name to [%s]" % (self.team1, self.team2))

	"""
	getTeams(self)
	SUMMARY: Gets current team names in the match
	PARAMETERS:
		NONE
	RETURNS list teams - list of length 2 with values [team1Name, team2Name]
	"""
	def getTeams(self):
		teams = [self.team1, self.team2] ##Create return list
		return teams

	"""
	getTeamString(self)
	SUMMARY: Gets the current teams in the match as a string
	PARAMETERS:
		NONE
	RETURNS string str - String of team names in format "{Team1Name}:{Team2Name}"
	"""
	def getTeamString(self):
		return str(self.team1 + ":" + self.team2)
	
	"""
	changeTeam1Score(self, delta)
	SUMMARY: Modifies team 1's current score
	PARAMETERS:
		delta - Integer to modify team 1's score by, can be positive or negative
	RETURNS VOID
	"""
	def changeTeam1Score(self, delta):
		self.score1 += int(delta) #int cast for potential user error
		print("Team 1's score had delta %i, score is now %i" % (delta, self.score1))
	
	"""
	changeTeam2Score(self, delta)
	SUMMARY: Modifies team 2's current score
	PARAMETERS:
		delta - Integer to modify team 2's score by, can be positive or negative
	RETURNS VOID
	"""
	def changeTeam2Score(self, delta):
		self.score2 += int(delta) #int cast for potential user error
		print("Team 2's score had delta %i, score is now %i" % (delta, self.score2))
	
	"""
	getTeam1Score(self)
	SUMMARY: gets Team 1's current score
	PARAMETERS:
		NONE
	RETURNS int score - Integer of team 1's current score
	"""
	def getTeam1Score(self):
		return self.score1
	
	"""
	getTeam2Score(self)
	SUMMARY: gets Team 2's current score
	PARAMETERS:
		NONE
	RETURNS int score - Integer of team 2's current score
	"""
	def getTeam2Score(self):
		return self.score2
	
	"""
	setMatchLength(self, length)
	SUMMARY: Sets the match length to the specified length in seconds
	PARAMETERS:
		int length - Integer of match length in seconds
	RETURNS VOID
	"""
	def setMatchLength(self, length):
		self.timeL = int(length)
	
	"""
	getMatchLength(self)
	SUMMARY: Gets the current match length
	PARAMETERS:
		NONE
	RETURNS int time - integer of match length
	"""
	def getMatchLength(self):
		return self.timeL
	
	"""
	getScores(self)
	SUMMARY: Gets the current scores
	PARAMETERS:
		NONE
	RETURNS tuple scores - tuple of the scores in form [team1Score, team2Score]
	"""
	def getScores(self):
		return self.score1, self.score2
	
"""
Class TimerSystem
SUMMARY: Provides functions for creating a timer for matches
INIT PARAMETERS:
	NONE
"""
class TimerSystem():
	def __init__(self):
		self.start = False
		self.pulser = False
		self.timeRem = 0
		self.matchLength = 20
	
	"""
	setMatchTime(self, setTime)
	SUMMARY: sets the match length to specified time in seconds
	PARAMETERS:
		int setTime - integer of desired match length in seconds
	RETURNS VOID
	"""
	def setMatchTime(self, setTime):
		self.matchLength = int(setTime)
	
	"""
	setTimeRemain(self, timeRemain)
	SUMMARY: Sets the remaining time in seconds for the match
	PARAMETERS:
		int timeRemain - integer of remaining time in seconds
	RETURNS VOID
	"""
	def setTimeRemain(self, timeRemain):
		self.timeRem = int(timeRemain)

	"""
	decrementTime(self)
	SUMMARY: decrements remaining time by 1 second
	PARAMETERS:
		NONE
	RETURNS VOID
	"""
	def decrementTime(self):
		self.timeRem -= 1
	
	"""
	getRemainingTime(self)
	SUMMARY: Gets the current remaining time in the match
	PARAMETERS:
		NONE
	RETURNS int timeRem - integer of remaining time of match in seconds
	"""
	def getRemainingTime(self):
		return self.timeRem
	
	"""
	setState(self, state)
	SUMMARY: sets the state of the timer. True will start the timer and False stops it.
	PARAMETERS:
		bool state - Boolean of state to set timer in
	RETURNS VOID
	"""
	def setState(self, state):
		self.start = bool(state)
		print("State is " + str(self.start))
		if self.start == True:
			self.timeRem = self.matchLength
		else:
			buzzerSound.play()
	
	"""
	getState(self)
	SUMMARY: gets the state of the timer
	PARAMETERS:
		NONE
	RETURNS: bool state - State of the timer. True = activated False = deactivated
	"""
	def getState(self):
		return self.start
	
	"""
	getPulser(self)
	SUMMARY: gets the state of the pulser variable
	PARAMETERS:
		NONE
	RETURNS bool pulser - Boolean value of the pulser
	"""
	def getPulser(self):
		return self.pulser
	
	"""
	setPulser(self, state)
	SUMMARY: sets the pulser variable to the specified boolean state
	PARAMETERS:
		bool state - Boolean state to set pulser variable to
	RETURNS VOID
	"""
	def setPulser(self, state):
		self.pulser = bool(state)

''''''#*****************************************************************************************************
''''''# ---[ Functions ]---
''''''#*****************************************************************************************************

"""
sendCmd(cmd)
SUMMARY: Sends a command to the server program (leaderboard)
PARAMETERS:
	cmd - string of command to send
RETURNS:
	Return value is command dependent!
		COMMAND = "NEXT_MATCH" 	-> RETURNS string teams - String of next match in format "Team1:Team2"
		COMMAND = OTHERS 		-> RETURNS VOID
"""
def sendCmd(cmd):

	# Send the command with ascii encoding to the UDP IP and PORT
	SOCK.sendto(cmd.encode('ascii'), (UDP_IP, UDP_PORT))

	# Recieve data back from the server if applicable
	if cmd.strip().upper() in recievingCmds:
		rawData, addr = SOCK.recvfrom(1024) # 1kB buffer size, should be plenty as each character is 1 byte, therefore room for 1024 characters
		strings = rawData.decode("ascii").strip().upper() # Decode the buffer
		print("Received from server '%s'" % strings)
		if strings.count(":") == 1: # Check for the splitting character
			teams = strings.split(":")
			return teams
		else:
			print("Received data back from server, but it wasnt formattable, so either match list is empty, or has 2 already queued")
			teams = ["NULL"]
			return teams

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
getDataFilePath()
SUMMARY: Gets the path to the data folder, use when accessing files like methods.txt
PARAMETERS:
	NONE
RETURNS: Path to data folder if the folder exists
"""
def getDataFilePath():
	scriptDir = os.path.dirname("__file__")
	dataFolder = "data" # name of the data folder
	path = os.path.join(scriptDir, dataFolder) # create a path variable for the data folder, referenced alot later
	if(os.path.exists(path) == True):
		return path
	else:
		print("Datafile still didn't exist!")
		raise FileNotFoundError("Datafile path does not exist? Check folder naming and try again.")

"""
saveCurrentMatch()
SUMMARY: saves the current match data to a session file for persistence
PARAMETERS:
	NONE
RETURNS VOID
"""
def saveCurrentMatch():
	print("Saving current match to session file so it can be loaded on net launch")
	if(os.path.isfile(getDataFilePath() + "/session.txt") == True):
		fileHandle = open(getDataFilePath() + "/session.txt", "w") # we are saving current name stuff
	else:
		fileHandle = open(getDataFilePath() + "/session.txt", "x") # we are saving current name stuff, but the file doesnt exist so we need to cerate it ("x" tag)
	teams = ScoreSystem.getTeamString() # get string of teams
	teamList = teams.split(":")
	fileHandle.write(teamList[0] + "\n")
	fileHandle.flush()
	fileHandle.write(teamList[1])
	fileHandle.flush()
	fileHandle.close()

"""
loadCurrentMatch()
SUMMARY: Loads saved match data from a session file
PARAMETERS:
	NONE
RETURNS list teams - List of team names
"""
def loadCurrentMatch():
	try:
		print("Attempting to load previous session data")
		if(os.path.isfile(getDataFilePath() + "/session.txt") == True):
			fileHandle = open(getDataFilePath() + "/session.txt", "r")
			teams = fileHandle.readlines()
			if len(teams) != 2:
				print("Teams file is empty or doesnt have enough teams in it (corrupted?)! returning File Error as teams")
				teams = ["File","Error"]
				return teams
			else:
				print("Well we haven't gotten an exception yet, so we must have loaded the file.")
				for index in range(0,len(teams)):
					teams[index] = teams[index].strip().upper() # Sanitization of input
				return teams
		else:
			print("File path didn't exist! Loading teams as File Missing...")
			teams = ["File", "Missing"]
			return teams

	except Exception as e:
		raise IndexError("Index Exception when loading session data!")
		print("Indexing did a oopsie")
		raise FileNotFoundError("File not found Error when loading session data! Blame Mechanical team.")
		print("No file found? Someone deleted or moved it, blame mechanical")
		raise e
		print("Error occured...")
		teams = ["Nil","Null"]
		return teams

"""
readScoreMethods()
SUMMARY: Reads the methods text file to generate a dictionary of scoring methods and their point value
PARAMETERS:
	NONE
RETURNS dict methodDict - Dictionary of methods, indexed by method name, containing point values
"""
def readScoreMethods():
	if(os.path.isfile(getDataFilePath() + "/methods.txt") == True):
		fileHandle = open(getDataFilePath() + "/methods.txt", "r")
		dataLines = fileHandle.readlines()
		fileHandle.close()
		methodDict = {}
		for line in dataLines:
			cooked = line.strip().upper()
			scoreMethod = constructScoreMethod(cooked)
			methodDict[scoreMethod[0]] = scoreMethod[1] # methodDict[method] = score
		return methodDict
	else:
		raise FileNotFoundError("Methods text file does not exist!!!")
		print("Methods file path does not exist!")

"""
readMethodNames()
SUMMARY: Reads the methods text file to create a list of method names
PARAMETERS:
	NONE
RETURNS: list methods - list of method names
"""
def readMethodNames():
	if(os.path.isfile(getDataFilePath() + "/methods.txt") == True):
		fileHandle = open(getDataFilePath() + "/methods.txt", "r")
		dataLines = fileHandle.readlines()
		fileHandle.close()
		index = 0
		methods = []
		for line in dataLines:
			cooked = line.strip().upper()
			cookedPan = cooked.split(":")
			methods.insert(index, cookedPan[0])
			index += 1
		return methods
	else:
		raise FileNotFoundError("Methods text file does not exist!!!")
		print("Methods file path does not exist!")

"""
constructScoreMethod(string)
SUMMARY: Constructs a scoring method by splitting the method string and integer apart
PARAMETERS:
	string string - String of a scoring method and its point value in format "Name:score"
RETURNS list cooked - list of scoring method of type ["method",int score]
"""
def constructScoreMethod(string): #AKA split the string, parse integer
	raw = string.split(":")
	print(raw)
	cooked = ["",0]
	cooked[0] = raw[0] # Method name is index 0
	try:
		cooked[1] = int(raw[1]) #cooked 1 is integer of point value
	except Exception as e:
		raise ValueError("Cannot Format")
		print("OwO wat dis?")
		raise e
		print("Weird stuff happened")
	return cooked

"""
handleSerialRead(data)
SUMMARY: Handles data from a serial event
PARAMETERS:
	string data - string of data from Serial event that may have a command in it
RETURNS VOID
"""
def handleSerialRead(data):
	strippedData = data.strip().upper()
	print("[COM] Stripped Data: %s   |   Raw: %s" % (strippedData, data))
	print("[COM] Receive complete, handling...")
	if strippedData == "S": #Start match COM data
		print("[COM] Start match event received. starting a match.")
		startTime = time.time() # setup the start time for the timer
		Time.setState(True) # Start the timer	
		updateMethod(0," ") # reset latest scoring method for team 1
		updateMethod(1," ") # reset latest scoring method for team 2
		ScoreSystem.changeTeam1Score(-ScoreSystem.getTeam1Score())#reset score for team 1
		ScoreSystem.changeTeam2Score(-ScoreSystem.getTeam2Score())#reset score for team 2
	elif strippedData == "E": #Stop match COM data
		print("[COM] Stopping match")
		Time.setState(False)
	elif strippedData == "N": #get next match COM data
		print("[COM] Getting next match")
		if(Time.getState() == False):
			teams = sendCmd("next_match")
			if len(teams) == 2:
				ScoreSystem.insertTeamNames(teams[0], teams[1])
		else:
			print("Match running, cant get new teams")
	else: # if it wasnt one of the above 3, it must be a score method
		print("[COM] Data was not a start match condition, checking scoring methods...")
		methods = readMethodNames()
		methodDict = readScoreMethods()
		i = 0
		for method in methods:
			if strippedData == str(method + "1"):
				print("[COM] Method \"%s\" has matched to team 1." % (strippedData))
				if Time.getState() == True:
					ScoreSystem.changeTeam1Score(methodDict[method])
					updateMethod(0,methods[i])
				else:
					print("Cant add score, match not going")
				break
			elif strippedData == str(method + "2"):
				print("[COM] Method \"%s\" has matched to team 2." % (strippedData))
				if Time.getState() == True:
					ScoreSystem.changeTeam2Score(methodDict[method])
					updateMethod(1,methods[i])
				else:
					print("Cant add score, match not going")
				break
			else:
				print("[COM] Method \"%s\" not matched yet." % (strippedData))
			i += 1
	print("[COM] Handle complete.")	

"""
readSerialConnection(ser)
SUMMARY: Threaded function for constant reading of the serial port
PARAMETERS:
	Serial ser - Serial port to read
RETURNS VOID
"""
def readSerialConnection(ser):
	while True:
		print("[COM] Awaiting...")
		reading = ser.readline().decode() # blocking until data is received, so if you send next_match and its waiting for data back, the GUI wont respond until such data arrives
		handleSerialRead(reading)
		
"""
updateMethod(index, methodIn)
SUMMARY: updates the recent scoring method for each team on the GUI
PARAMETERS:
	int index - integer of method to modify
	string methodIn - string of method to write
RETURN VOID
"""
def updateMethod(index, methodIn):
	method[index] = methodIn

''''''#*****************************************************************************************************
''''''# ---[ MAIN CODE BEGINS HERE ]---
''''''#*****************************************************************************************************

## Begin Serial Port connection code

print("Listing COM ports:")
for port in serial.tools.list_ports.comports():
	print(port)
	time.sleep(0.1)

print("COM ports listed. Attempting to find an Arduino...")
arduinoPorts = [ port.device for port in serial.tools.list_ports.comports() ] # if "Arduino" in port.description
if not arduinoPorts:
	raise IOError("No Arduino Found!")
if len(arduinoPorts) > 1:
	warnings.warn("Multiple Arduinos were found - using first option")

print("Connecting to Arduino...")
ser = serial.Serial(arduinoPorts[0]) #establish connection to COM port

serialThread = threading.Thread(target=readSerialConnection, args=(ser,)) # Create a thread for handling serial data events
serialThread.daemon = True # Setup the thread as a daemon so that it will exit when the main program closes
serialThread.start() # Start the serial data thread

## End Serial Port connection code


## ---[ PyGame Initialization ]---

pygame.init() #Initialize PyGame So we can make a GUI

## Load Sound Effects
buzzerSound = pygame.mixer.Sound(getDataFilePath() + "/buzzer.wav") # load buzzer sound

# Window Parameters
WINDOW_WIDTH	= 1920
WINDOW_HEIGHT	= 1080
xUnit			= WINDOW_WIDTH // 16 # make a sweet grid system - X axis
yUnit			= WINDOW_HEIGHT // 9 # make a sweet grid system - Y axis
DISPLAY_SURFACE	= pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))#, pygame.FULLSCREEN) <-- uncomment for fullscreen application
pygame.display.set_caption("Battle BABs - Client")

# Fonts
LARGE_FONT	= pygame.font.SysFont("monospace", 52, True)
MEDIUM_FONT	= pygame.font.SysFont("monospace", 36, True)
SMALL_FONT	= pygame.font.SysFont("monospace", 24, True)

# Colours   R    G    B
C_LGRAY	= ( 72,  96, 112)
C_MGRAY	= ( 48,  64,  80)
C_DGRAY	= ( 28,  36,  44)
C_GRAY1	= ( 52,  72,  88)
C_GRAY2	= ( 60,  80,  96)
C_CYAN	= ( 32, 196, 220)
C_MINT	= ( 32, 255, 196)

# Rectangles       COLOR  ,                   PYGAME RECTANGLE
R_SEP_C		    = (C_GRAY2,	pygame.Rect(xUnit * 2,  yUnit * 0,  xUnit * 1,  yUnit * 9 )) # Rectangle to Seperate Title and Stats
R_SCOREBOARD_R	= (C_DGRAY,	pygame.Rect(xUnit * 3,  yUnit * 0,  xUnit * 13, yUnit * 1 )) # Rectangle for Match name
R_TITLE_C		= (C_DGRAY,	pygame.Rect(xUnit * 0,  yUnit * 0,  xUnit * 2,  yUnit * 5 )) # Rectangle for Battle BABs title
R_CONTROL_C		= (C_CYAN,	pygame.Rect(xUnit * 0,  yUnit * 5,  xUnit * 2,  yUnit * 4 )) # Rectangle under Title Text
R_TIMETITLE_R   = (C_LGRAY,	pygame.Rect(xUnit * 7, 	yUnit * 1, 	xUnit * 5,	yUnit * 1 )) # Rectangle for Time Remaining
R_BORDER_C      = (C_MGRAY, pygame.Rect(xUnit * 3, 	yUnit * 1, 	xUnit * 13,	yUnit * 1 )) # Rectangle for Horizontal Border
R_TEAM1_R       = (C_LGRAY, pygame.Rect(xUnit * 4, 	yUnit * 3, 	xUnit * 4,	yUnit * 1 )) # Rectangle for Team 1's Name
R_TEAM2_R       = (C_LGRAY, pygame.Rect(xUnit * 11,	yUnit * 3, 	xUnit * 4,	yUnit * 1 )) # Rectangle for Team 2's Name
R_SCORE1_R      = (C_LGRAY, pygame.Rect(xUnit * 4,	yUnit * 4, 	xUnit * 4,	yUnit * 1 )) # Rectangle for Team 1's Score
R_SCORE2_R      = (C_LGRAY, pygame.Rect(xUnit * 11, yUnit * 4, 	xUnit * 4,	yUnit * 1 )) # Rectangle for Team 2's Score
R_METHOD1_R     = (C_LGRAY, pygame.Rect(xUnit * 4, yUnit * 5, 	xUnit * 4,	yUnit * 1 )) # rectangle for Team 1's scoring method
R_METHOD2_R     = (C_LGRAY, pygame.Rect(xUnit * 11,	yUnit * 5, 	xUnit * 4,	yUnit * 1 )) # Rectangle for Team 2's scoring method

# Scorekeeping and Countdown System
__MatchLength = 120 # Change this variable's value to adjust the length of a match in seconds. Must be an integer!

Time = TimerSystem() # Create an instance of the TimerSystem class
ScoreSystem = MatchFramework("", "", __MatchLength) # Create an instance of the MatchFramework class

teams = ["Null", "Null"] #Teams List: Holder of the Team Names
scores = ["0", "0"] #Scores List: Holder of the Scores
method = ["Null", "Null"] #Method List: Holder of the Latest Scoring method

startTime = time.time() # Get initial time

Time.setMatchTime(ScoreSystem.getMatchLength()) # Set the inital match time

teams = loadCurrentMatch() # Load a saved session
ScoreSystem.insertTeamNames(teams[0], teams[1])

''''''#*****************************************************************************************************
''''''# ---[ MAIN LOOP ]---
''''''#*****************************************************************************************************

while True: #Main Loop
	teams = ScoreSystem.getTeams()
	matchState = Time.getState()
	# Match Timer Countdown handling
	if matchState == True:
		enlapsed = time.time() - startTime
		if enlapsed >= 1:
			if Time.getRemainingTime() > 1:
				startTime = time.time()
				print("1 second Ping at: " + str(enlapsed))
				Time.decrementTime()
			else:
				Time.setTimeRemain(0)
				Time.setState(False)
				Time.setPulser(True)
	# Match time stuff complete

	DISPLAY_SURFACE.fill(C_DGRAY) # "Clear" the Screen
	pygame.draw.rect(DISPLAY_SURFACE, *R_SEP_C)
	pygame.draw.rect(DISPLAY_SURFACE, *R_CONTROL_C)
	pygame.draw.rect(DISPLAY_SURFACE, *R_BORDER_C)
	pygame.draw.rect(DISPLAY_SURFACE, *R_TIMETITLE_R)
	pygame.draw.rect(DISPLAY_SURFACE, *R_TEAM1_R)
	pygame.draw.rect(DISPLAY_SURFACE, *R_TEAM2_R)
	pygame.draw.rect(DISPLAY_SURFACE, *R_SCORE1_R)
	pygame.draw.rect(DISPLAY_SURFACE, *R_SCORE2_R)
	pygame.draw.rect(DISPLAY_SURFACE, *R_METHOD1_R)
	pygame.draw.rect(DISPLAY_SURFACE, *R_METHOD2_R)
	

	blitInRect(R_TIMETITLE_R[1], MEDIUM_FONT, C_MINT, "Match Time Remaining:", str(Time.getRemainingTime()) + " Seconds") # The "999" is just there as a placeholder for a timer variable
	blitInRect(R_TITLE_C[1], LARGE_FONT, C_MINT, "Battle", "BABs", time.strftime("%Y"))
	blitInRect(R_SCOREBOARD_R[1], MEDIUM_FONT, C_MINT, "Match: [" + teams[0] + "] VS [" + teams[1] + "]")
	blitInRect(R_TEAM1_R[1], MEDIUM_FONT, C_MINT, teams[0])
	blitInRect(R_TEAM2_R[1], MEDIUM_FONT, C_MINT, teams[1])
	scores = ScoreSystem.getScores()
	blitInRect(R_SCORE1_R[1], MEDIUM_FONT, C_MINT, str(scores[0]))
	blitInRect(R_SCORE2_R[1], MEDIUM_FONT, C_MINT, str(scores[1]))
	blitInRect(R_METHOD1_R[1], MEDIUM_FONT, C_MINT, method[0])
	blitInRect(R_METHOD2_R[1], MEDIUM_FONT, C_MINT, method[1])
	
	pygame.display.update() #Update display
	if Time.getPulser() == True and Time.getState() == False:
		sendCmd(teams[0] + ":" + str(scores[0]) + "," + teams[1] + ":" + str(scores[1]))
		Time.setPulser(False)
	
	for event in pygame.event.get(): #Event handling to take care of "Hanging" issues with OS
		if event.type == pygame.QUIT: #Check for QUIT event
			saveCurrentMatch()
			print("Quitting.")
			pygame.quit() #quit if so
			quit()
		elif event.type == pygame.KEYDOWN: # KEYDOWN Events, mainly for debugging reasons
			if event.key == pygame.K_n:
				if(Time.getState() == False):
					teams = sendCmd("next_match")
					if len(teams) == 2:
						ScoreSystem.insertTeamNames(teams[0], teams[1])
				else:
					print("Match running, cant get new teams")

			elif event.key == pygame.K_f: # Force send match over data
				sendCmd(teams[0] + ":" + str(scores[0]) + "," + teams[1] + ":" + str(scores[1]))

			elif event.key == pygame.K_PERIOD: # Debug add 1 point to team 2
				if matchState == True:
					ScoreSystem.changeTeam2Score(1)
					updateMethod(1,"ADMIN+") # reset latest scoring method for team 1

			elif event.key == pygame.K_PERIOD: # Debug sub 1 point to team 2
				if matchState == True:
					ScoreSystem.changeTeam2Score(-1)
					updateMethod(1,"ADMIN-") # reset latest scoring method for team 1

			elif event.key == pygame.K_COMMA: # Debug add 1 point to team 1
				if matchState == True:
					ScoreSystem.changeTeam1Score(1)
					updateMethod(0,"ADMIN+") # reset latest scoring method for team 1
			
			elif event.key == pygame.K_x: # Debug sub 1 point to team 1
				if matchState == True:
					ScoreSystem.changeTeam1Score(-1)
					updateMethod(0,"ADMIN-") # reset latest scoring method for team 1

			elif event.key == pygame.K_SPACE: # Debug start match
				Time.setState(True)
				startTime = time.time()
				updateMethod(0," ") # reset latest scoring method for team 1
				updateMethod(1," ") # reset latest scoring method for team 2
				ScoreSystem.changeTeam1Score(-ScoreSystem.getTeam1Score())#reset score for team 1
				ScoreSystem.changeTeam2Score(-ScoreSystem.getTeam2Score())#reset score for team 2

			elif event.key == pygame.K_b: # debug stop match without match send
				Time.setState(False) # debug match stop

	time.sleep(0.02) #delay 20ms to prevent CPU usage