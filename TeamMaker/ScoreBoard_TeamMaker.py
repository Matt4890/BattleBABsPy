import os
import sys
import time

def getDataFilePath():
	scriptDir = os.path.dirname("__file__")
	dataFolder = "data"
	path = os.path.join(scriptDir, dataFolder)
	return path

def getInputLines():
    fileHandle = open(getDataFilePath() + "/input.txt", "r") # open the input file in read mode
    lines = fileHandle.readlines()
    fileHandle.close()
    return lines

def constructTeams(teamNames):
    i = 0
    teamList = []
    for name in teamNames:
        teamData = str(name.strip().upper() + ":0:0:0:0\n")
        teamList.insert(i,teamData)
        i += 1
    return teamList

def writeOutput(teamList):
    fileHandle = open(getDataFilePath() + "/teams.txt", "w")
    fileHandle.writelines(teamList)
    fileHandle.flush()
    fileHandle.close()

print("\n\nCreating a teams text file for use with the Scoreboard Server Python Program.")
print("Reading input file...")
inputLines = getInputLines()
if len(inputLines) > 0:
    print("Constructing a list of new team data...")
    teamList = constructTeams(inputLines)
    print("Writing team data to text file...")
    writeOutput(teamList)
    print("Complete.")
else:
    print("\n\n\n[ERROR]: Input text file had no lines in it! I cant make team data out of thin air!")
    print("[SOLUTION]: Insert Team names into the file \"input.txt\"\n\n\n")

print("Exitting in 3 seconds...\n\n")
time.sleep(3)
exit()