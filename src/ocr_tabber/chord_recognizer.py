#!/usr/bin/env python3
# Copyright 2014 Utkarsh Jaiswal
# Updated 2026 - Modernized for Python 3

"""
Uses the output of ocr-tab.py to check for and recognize chords
in input ASCII tabs from a pre-existing database.
"""

import pickle
import sys
from operator import itemgetter
from pathlib import Path
from typing import List, Tuple, Optional


class ChordRecognizer:
    """Recognizes guitar chords from ASCII tablature."""

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize the chord recognizer with a chord database.

        Args:
            db_path: Path to the pickled chord database. If None, uses default location.
        """
        if db_path is None:
            # Default path relative to package
            db_path = Path(__file__).parent.parent.parent / "data" / "mainDB.pkl"

        if not db_path.exists():
            raise FileNotFoundError(f"Chord database not found: {db_path}")

        # Load database once during initialization (performance fix)
        with open(db_path, "rb") as infile:
            self.chord_db = pickle.load(infile)

    def recognize_chord(
        self, key: List[str], chord_notes: List[List[int]]
    ) -> Optional[str]:
        """
        Run the set of notes against the database to identify the chord.

        Args:
            key: List of string tunings (e.g., ['E', 'A', 'D', 'G', 'B', 'E'])
            chord_notes: List of [string_no, fret_no, position] triplets

        Returns:
            The chord name if recognized, None otherwise
        """
        if not chord_notes:
            return None

        # Build chord string from thickest to thinnest string
        chord = ""
        for i in range(len(chord_notes) - 1, -1, -1):
            string_no = chord_notes[i][0]
            fret_no = chord_notes[i][1]
            chord += f"{key[string_no - 1]} {fret_no} "

        # Search database for matching chord
        chord_set = [x[1] for x in self.chord_db]

        if chord in chord_set:
            index = chord_set.index(chord)
            chord_name = self.chord_db[index][0]
            print(f"Chord recognized - {chord_name}")

            # Suggest alternate chord fingerings
            print("Alternate fingerings:")
            for entry in self.chord_db:
                if entry[0] == chord_name:
                    print(f"  {entry[1]}")

            return chord_name

        return None


def parse_ascii_tab(tab_path: Path) -> Tuple[List[str], List[List[int]]]:
    """
    Parse ASCII tab file to extract key and note positions.

    Args:
        tab_path: Path to ASCII tab file

    Returns:
        Tuple of (key, all_notes) where:
        - key: List of string tunings
        - all_notes: List of [string_no, fret_no, position] triplets
    """
    key = []  # Tuning of each string
    allowed_key = set("abcdefgABCDEFG")
    all_notes = []
    string_count = 1

    with open(tab_path, encoding="utf-8") as infile:
        for line in infile:
            if string_count > 6:
                string_count = 1

            if line and line[0] in allowed_key:
                line_pos = []
                key.append(line[0].upper())
                line_notes = line.replace("|", " ").replace("\\", " ").split("-")

                count = 0
                for note in line_notes:
                    count += 1
                    if note.isdigit():
                        line_pos.append(count)

                line_notes = [int(x) for x in line_notes if x.isdigit()]

                for i in range(len(line_notes)):
                    all_notes.append([string_count, line_notes[i], line_pos[i]])

                string_count += 1

    # Sort by position (column) in the tab
    all_notes = sorted(all_notes, key=itemgetter(2))

    return key, all_notes


def find_chords_in_tab(
    key: List[str], all_notes: List[List[int]], recognizer: ChordRecognizer
) -> List[str]:
    """
    Identify chords in parsed tab by finding notes played simultaneously.

    Args:
        key: List of string tunings
        all_notes: List of [string_no, fret_no, position] triplets
        recognizer: ChordRecognizer instance

    Returns:
        List of recognized chord names
    """
    recognized_chords = []
    chord_notes = []
    i = 0

    while i < len(all_notes) - 1:
        x = all_notes[i]
        y = all_notes[i + 1]

        if x[2] == y[2]:  # Notes are at same position (played together)
            chord_notes.append(x)
            chord_notes.append(y)
            i += 1

            if i < len(all_notes) - 1:
                y = all_notes[i + 1]

            # Continue collecting notes at the same position
            while x[2] == y[2] and i < len(all_notes) - 1:
                chord_notes.append(y)
                i += 1
                if i < len(all_notes) - 1:
                    y = all_notes[i + 1]

        if chord_notes:
            chord_name = recognizer.recognize_chord(key, chord_notes)
            if chord_name:
                recognized_chords.append(chord_name)
            chord_notes = []

        i += 1

    return recognized_chords


def main() -> int:
    """
    Main entry point for the chord-recognizer command-line tool.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    if len(sys.argv) < 2:
        print("Usage: chord-recognizer <ascii_tab_file>", file=sys.stderr)
        print("Example: chord-recognizer data/ASCIItab.txt", file=sys.stderr)
        return 1

    tab_path = Path(sys.argv[1])

    if not tab_path.exists():
        print(f"Error: Tab file not found: {tab_path}", file=sys.stderr)
        return 1

    try:
        # Initialize recognizer (loads database once)
        recognizer = ChordRecognizer()

        # Parse the ASCII tab
        key, all_notes = parse_ascii_tab(tab_path)

        if not key:
            print("Error: No valid guitar strings found in tab", file=sys.stderr)
            return 1

        print(f"Detected tuning: {' '.join(key)}")
        print(f"Found {len(all_notes)} notes in tab")
        print("\nSearching for chords...\n")

        # Find and recognize chords
        recognized_chords = find_chords_in_tab(key, all_notes, recognizer)

        if not recognized_chords:
            print("No chords recognized in this tab.")

        return 0

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
