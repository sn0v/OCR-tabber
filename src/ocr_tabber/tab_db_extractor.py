# Copyright 2014 Utkarsh Jaiswal

# Utility script to parse the XML chord database packaged with Gnome Guitar (http://gnome-chord.sourceforge.net/)
# It extracts relevant info (chord names, fret positions) while leaving out the rest
# Fret positions are always extracted from thickest to thinnest string (EADGBE for standard E tuning)

import xml.etree.ElementTree as ET
import json
import pickle

tree = ET.parse('../data/mainDB.xml') # input database (XML format)
root = tree.getroot()

# A dictionary can't be used here since the database contains multiple fingerings for each chord
chordList = [] 

for child in root: # attribute - chord
	chordName = child.attrib['name']
	
	# A dictionary can't be used here since multiple strings are often tuned to the same note, albeit in different octaves
	# Hence, unique keys aren't possible
	# Instead, a single string is used with whitespaces
	# Eg - The C major chord will be denoted as 'E None A 3 D 2 G 0 B 1 E 0'
	chordFrets = ''
	for gStr in child.findall('./voiceing/guitarString'):
		# append the string tuning and fret number to the fret data for the current chord
		if (gStr[2].text):
			chordFrets += str(gStr[0].text) + ' ' + str(gStr[2].text) + ' '

	chordList.append([chordName, chordFrets])

#for item in chordList:
#	print item[0], ',', item[1]

#print len(chordList)

# Pickle the chord list to file
with open('../data/mainDB.pkl', 'wb') as outfile:
	pickle.dump(chordList, outfile)
