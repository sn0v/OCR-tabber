# Copyright 2014 Utkarsh Jaiswal 

# Uses the output of ocr-tab.py
# Checks for and recognizes chords in input ASCII tabs from a pre-existing database.

from operator import itemgetter

key = [] # key of current tab
allowedKey = ['a','b','c','d','e','f','g','A','B','C','D','E','F','G'] # list of allowed tunings for strings
allNotes = [] # list of all fret numbers and their corresponding positions (from the left) on that string
# allNotes consists of a list of all (fret no, position) pairs in the tab 
stringCount = 1

with open("../data/ASCIItab.txt") as infile:
	for line in infile:
		if (stringCount > 6): # reset it
			stringCount = 1
		if (line[0] in allowedKey): # this line contains valid tabs for a string
			linePos = [] # positions of all notes played on that string
			key.append(line[0]) # scan first character for string tuning
			lineNotes = line.replace('|', ' ').replace('\\', ' ').split('-')
			count = 0
			for note in lineNotes:
				count += 1
				if note.isdigit():
					linePos.append(count)
			lineNotes = [int(x) for x in lineNotes if x.isdigit()]
			for i in range(len(lineNotes)):
				allNotes.append([stringCount, lineNotes[i], linePos[i]])
			stringCount += 1

#allNotes = sorted(allNotes, key=itemgetter(1))
print allNotes

# Clean up key (tuning info)
for char in key:
	if not char.isalpha(): # remove non alphabetical characters (possible errors)
		key.remove(char)
key = key[0:6] # ensure a length of 6 since only six strings exist
print key

