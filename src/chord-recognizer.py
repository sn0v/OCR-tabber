# Copyright 2014 Utkarsh Jaiswal 

# Uses the output of ocr-tab.py
# Checks for and recognizes chords in input ASCII tabs from a pre-existing database.

import re

key = []
allNotes = [] # list of all fret numbers and their corresponding positions (from the left) on that string
# allNotes consists of a list of all (fret no, position) pairs in the tab 
with open("../data/ASCIItab.txt") as infile:
	for line in infile:
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
			allNotes.append([lineNotes[i], linePos[i]])

print allNotes

# Clean up key (tuning info)
for char in key:
	if not char.isalpha(): # remove non alphabetical characters (possible errors)
		key.remove(char)
key = key[0:6] # ensure a length of 6 since only six strings exist
print key

