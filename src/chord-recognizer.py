# Copyright 2014 Utkarsh Jaiswal 

# Uses the output of ocr-tab.py
# Checks for and recognizes chords in input ASCII tabs from a pre-existing database.

from operator import itemgetter
import pickle

key = [] # key of current tab
allowedKey = ['a','b','c','d','e','f','g','A','B','C','D','E','F','G'] # list of allowed tunings for strings
allNotes = [] # list of all string numbers, fret numbers and their corresponding positions (from the left) on that string
# allNotes consists of a list of all (string no, fret no, position) triplets in the tab 
stringCount = 1

# prepare a list of all notes and their positions in the input tab
with open("../data/ASCIItab.txt") as infile:
	for line in infile:
		if (stringCount > 6): # reset it
			stringCount = 1
		if (line[0] in allowedKey): # this line contains valid tabs for a string
			linePos = [] # positions of all notes played on that string
			key.append(line[0].upper()) # scan first character for string tuning
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

allNotes = sorted(allNotes, key=itemgetter(2)) # sort by position of individual notes 
print allNotes, len(allNotes)
print key

# Run the set of notes passed to it (for a single chord) against the database
# to see if it matches any chords
def chordRecognition(key, chordNotes):
	with open("../data/mainDB.pkl", "rb") as infile: # load chord database from file
		chordDB = pickle.load(infile)
	chord = ''
	i = len(chordNotes) - 1
	while i >= 0:
		chord += key[chordNotes[i][0] - 1] + ' ' + str(chordNotes[i][1]) + ' '
		i -= 1
	print chord
		

# Check for presence of chords
# On the sorted list of notes, this is achieved by checking successive tuples to see if notes from different strings
# are equidistant from the left, ie are played at the same time
chordNotes = [] # (string no, fret no) pairs for chords
i = 0
while (i < len(allNotes) - 1):
	x = allNotes[i]
	y = allNotes[i+1]
	if (x[2] == y[2]): # both are equidistant from the left
		chordNotes.append(x)
		chordNotes.append(y)
		i += 1
		if (i < len(allNotes) - 1):
			y = allNotes[i+1]
		while (x[2] == y[2] and i < len(allNotes) - 1):
			chordNotes.append(y)
			i += 1
			if (i < len(allNotes) - 1):
				y = allNotes[i+1]
	chordRecognition(key, chordNotes) # notes for one chord have been extracted, recognize it
	i += 1
	print 'chordNotes ', chordNotes
	chordNotes = []
