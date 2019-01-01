"""
This is a terminal-based client for BattleBABs.
It runs in a terminal, sending commands to the server that are input via stdin.
Commands may be strung together in one line using the pipe '|' character.

Author: Matthew Allwright
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
			global NAME1 #not the neatest way to do this, will modify later, just need working system for testing
			global NAME2
			NAME1 = teams[0]
			NAME2 = teams[1]
			print("Name1: " + NAME1 + "\t Name2: " + NAME2)

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

pygame.init() #Initialize PyGame

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

NAME1 = "123456789ABCDEF"
NAME2 = "Team2GoesHere"

# Rects
R_SEP_C		    = (C_GRAY2,	pygame.Rect(xUnit * 2,  yUnit * 0,  xUnit * 1,  yUnit * 9 )) # Rectangle to Seperate Title and Stats
R_SCOREBOARD_R	= (C_DGRAY,	pygame.Rect(xUnit * 3,  yUnit * 0,  xUnit * 13, yUnit * 1 )) # Rectangle for Match name
R_TITLE_C		= (C_DGRAY,	pygame.Rect(xUnit * 0,  yUnit * 0,  xUnit * 2,  yUnit * 5 )) # Rectangle for Battle BABs title
R_CONTROL_C		= (C_CYAN,	pygame.Rect(xUnit * 0,  yUnit * 5,  xUnit * 2,  yUnit * 4 )) # Rectangle under Title Text
R_TIMETITLE_R   = (C_LGRAY,	pygame.Rect(xUnit * 7, 	yUnit * 1, 	xUnit * 5,	yUnit * 1 )) # Rectangle for Time Remaining
R_BORDER_C      = (C_MGRAY, pygame.Rect(xUnit * 3, 	yUnit * 1, 	xUnit * 13,	yUnit * 1 )) # Rectangle for Horizontal Border
R_TEAM1_R       = (C_LGRAY, pygame.Rect(xUnit * 4, 	yUnit * 3, 	xUnit * 4,	yUnit * 1 )) # Rectangle for Team 1's Name
R_TEAM2_R       = (C_LGRAY, pygame.Rect(xUnit * 11,	yUnit * 3, 	xUnit * 4,	yUnit * 1 )) # Rectangle for Team 2's Name

while True: #Main Loop
	DISPLAY_SURFACE.fill(C_DGRAY) # "Clear" the Screen
	pygame.draw.rect(DISPLAY_SURFACE, *R_SEP_C)
	pygame.draw.rect(DISPLAY_SURFACE, *R_CONTROL_C)
	pygame.draw.rect(DISPLAY_SURFACE, *R_BORDER_C)
	pygame.draw.rect(DISPLAY_SURFACE, *R_TIMETITLE_R)
	pygame.draw.rect(DISPLAY_SURFACE, *R_TEAM1_R)
	pygame.draw.rect(DISPLAY_SURFACE, *R_TEAM2_R)
	

	blitInRect(R_TIMETITLE_R[1], MEDIUM_FONT, C_MINT, "Match Time Remaining:", "999" + " Seconds") # The "999" is just there as a placeholder for a timer variable
	blitInRect(R_TITLE_C[1], LARGE_FONT, C_MINT, "Battle", "BABs", time.strftime("%Y"))
	blitInRect(R_SCOREBOARD_R[1], MEDIUM_FONT, C_MINT, "Match: [" + NAME1 + "] VS [" + NAME2 + "]")
	blitInRect(R_TEAM1_R[1], MEDIUM_FONT, C_MINT, NAME1)
	blitInRect(R_TEAM2_R[1], MEDIUM_FONT, C_MINT, NAME2)

	pygame.display.update() #Update display

	for event in pygame.event.get(): #Event handling to take care of "Hanging" issues with OS
		if event.type == pygame.QUIT: #Check for QUIT event
			pygame.quit() #quit if so
			quit()
		elif event.type == pygame.KEYDOWN: ##ease of testing events while keeping the GUI from crashing
			if event.key == pygame.K_n:
				sendCmd("next_match")
			elif event.key == pygame.K_r:
				sendCmd("reset")
			elif event.key == pygame.K_s:
				sendCmd("reset_scores")
			elif event.key == pygame.K_m:
				sendCmd("reset_matches")
	time.sleep(0.02) #delay 20ms to prevent CPU usage
	"""
	for line in sys.stdin:
		for cmd in line.split('|'):
			sendCmd(cmd)
	"""


