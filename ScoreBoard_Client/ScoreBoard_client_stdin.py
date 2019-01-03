"""
This is a terminal-based client for BattleBABs.
It runs in a terminal, sending commands to the server that are input via stdin.
Commands may be strung together in one line using the pipe '|' character.

Author: Matthew Allwright
Modified By: Not Matthew Allwright :P
"""

''''''#
''''''# Imports
''''''#

import socket
import sys
import pygame
import time


''''''#
''''''# Networking
''''''#

UDP_IP = "255.255.255.255" #IP is UDP Broadcast
UDP_PORT = 5005

SOCK = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
SOCK.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST,1)

# List of commands that should expect a message back from the server
recievingCmds = ["NEXT_MATCH"]
''''''#
''''''# Classes
''''''#

class MatchFramework():
	def __init__(self, team1 = "Team 1", team2 = "Team 2", startTime = 15):
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
	
	def insertTeamNames(self, team1Name, team2Name):
		self.team1 = team1Name
		self.team2 = team2Name
		print("Set team 1 name to [%s] and team 2 name to [%s]" % (self.team1, self.team2))
	
	def changeTeam1Score(self, delta):
		self.score1 += delta
		print("Team 1's score had delta %i, score is now %i" % (delta, self.score1))
	
	def changeTeam2Score(self, delta):
		self.score2 += delta
		print("Team 2's score had delta %i, score is now %i" % (delta, self.score2))
	
	def setMatchLength(self, length):
		self.timeL = length
	
	def getMatchLength(self):
		return self.timeL
	
	def getScores(self):
		return self.score1, self.score2
	

class TimerSystem():
	def __init__(self):
		self.start = False
		self.pulser = False
		self.timeRem = 0
		self.matchLength = 20
	
	def setMatchTime(self, setTime):
		self.matchLength = setTime
	
	def setTimeRemain(self, timeRemain):
		self.timeRem = timeRemain

	def decrementTime(self):
		self.timeRem -= 1
	
	def getRemainingTime(self):
		return self.timeRem
	
	def setState(self, state):
		self.start = state
		print("State is " + str(self.start))
		if self.start == True:
			self.timeRem = self.matchLength
	
	def getState(self):
		return self.start
	
	def getPulser(self):
		return self.pulser
	
	def setPulser(self, state):
		self.pulser = state

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
		strings = rawData.decode("ascii").strip().upper()
		print("Received from server '%s'" % strings)
		if strings.count(":") == 1:
			teams = strings.split(":")
			return teams

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

''''''#
''''''# Client Loop
''''''#

pygame.init() #Initialize PyGame So we can make a GUI

# Window Parameters
WINDOW_WIDTH	= 1920
WINDOW_HEIGHT	= 1080
xUnit			= WINDOW_WIDTH // 16 # make a sweet grid system - X axis
yUnit			= WINDOW_HEIGHT // 9 # make a sweet grid system - Y axis
DISPLAY_SURFACE	= pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))#, pygame.FULLSCREEN) <-- Use for fullscreen
pygame.display.set_caption("Battle BABs - Client")

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

# Scorekeeping and Countdown System
Time = TimerSystem() #Main Timer System
Time.daemon = True # Will kill on main thread exit
#Time.run() #bad thing happen with this uncommented
ScoreSystem = MatchFramework("TeamName1", "TeamName2", 20) # Create Scoring System from a MatchFramework
teams = ["Null", "Null"] #Teams List: Holder of the Team Names
scores = ["Null", "Null"] #Scores List: Holder of the Scores
startTime = time.time()

Time.setMatchTime(ScoreSystem.getMatchLength()) #match time set

while True: #Main Loop
	matchState = Time.getState()
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
	DISPLAY_SURFACE.fill(C_DGRAY) # "Clear" the Screen
	pygame.draw.rect(DISPLAY_SURFACE, *R_SEP_C)
	pygame.draw.rect(DISPLAY_SURFACE, *R_CONTROL_C)
	pygame.draw.rect(DISPLAY_SURFACE, *R_BORDER_C)
	pygame.draw.rect(DISPLAY_SURFACE, *R_TIMETITLE_R)
	pygame.draw.rect(DISPLAY_SURFACE, *R_TEAM1_R)
	pygame.draw.rect(DISPLAY_SURFACE, *R_TEAM2_R)
	pygame.draw.rect(DISPLAY_SURFACE, *R_SCORE1_R)
	pygame.draw.rect(DISPLAY_SURFACE, *R_SCORE2_R)
	

	blitInRect(R_TIMETITLE_R[1], MEDIUM_FONT, C_MINT, "Match Time Remaining:", str(Time.getRemainingTime()) + " Seconds") # The "999" is just there as a placeholder for a timer variable
	blitInRect(R_TITLE_C[1], LARGE_FONT, C_MINT, "Battle", "BABs", time.strftime("%Y"))
	blitInRect(R_SCOREBOARD_R[1], MEDIUM_FONT, C_MINT, "Match: [" + teams[0] + "] VS [" + teams[1] + "]")
	blitInRect(R_TEAM1_R[1], MEDIUM_FONT, C_MINT, teams[0])
	blitInRect(R_TEAM2_R[1], MEDIUM_FONT, C_MINT, teams[1])
	scores = ScoreSystem.getScores()
	blitInRect(R_SCORE1_R[1], MEDIUM_FONT, C_MINT, str(scores[0]))
	blitInRect(R_SCORE2_R[1], MEDIUM_FONT, C_MINT, str(scores[1]))
	
	pygame.display.update() #Update display
	if Time.getPulser() == True and Time.getState() == False:
		sendCmd(teams[0] + ":" + str(scores[0]) + "," + teams[1] + ":" + str(scores[1]))
		Time.setPulser(False)
	
	for event in pygame.event.get(): #Event handling to take care of "Hanging" issues with OS
		if event.type == pygame.QUIT: #Check for QUIT event
			pygame.quit() #quit if so
			quit()
		elif event.type == pygame.KEYDOWN: ## Ease of testing events while keeping the GUI from crashing
			if event.key == pygame.K_n:
				teams = sendCmd("next_match")
				ScoreSystem.insertTeamNames(teams[0], teams[1])
			elif event.key == pygame.K_r:
				sendCmd("reset")
			elif event.key == pygame.K_s:
				sendCmd("reset_scores")
			elif event.key == pygame.K_m:
				sendCmd("reset_matches")
			elif event.key == pygame.K_f: #Debug force send match completion
				sendCmd(teams[0] + ":" + str(scores[0]) + "," + teams[1] + ":" + str(scores[1]))
			elif event.key == pygame.K_PERIOD:
				if matchState == True:
					ScoreSystem.changeTeam2Score(1) #Debug add 1 to score 2
			elif event.key == pygame.K_COMMA:
				if matchState == True:
					ScoreSystem.changeTeam1Score(1) #Debug add 1 to score 1
			elif event.key == pygame.K_SPACE:
				Time.setState(True)
				startTime = time.time()
			elif event.key == pygame.K_b:
				Time.setState(False) # debug match stop

	time.sleep(0.02) #delay 20ms to prevent CPU usage
	"""
	for line in sys.stdin:
		for cmd in line.split('|'):
			sendCmd(cmd)
	"""


