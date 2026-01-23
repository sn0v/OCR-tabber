# Uses the output of ocr_tab.py
# Checks for and recognizes chords in input ASCII tabs from a pre-existing database.

import pickle
import sys
from operator import itemgetter
from pathlib import Path

# Get the data directory path relative to this module
DATA_DIR = Path(__file__).parent.parent.parent / "data"
ASCII_TAB_PATH = DATA_DIR / "ASCIItab.txt"
CHORD_DB_PATH = DATA_DIR / "mainDB.pkl"

# List of allowed tunings for strings
ALLOWED_KEY = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'A', 'B', 'C', 'D', 'E', 'F', 'G']


def load_chord_database(db_path: Path = CHORD_DB_PATH) -> list:
    """
    Load the chord database from a pickle file.

    Args:
        db_path: Path to the chord database pickle file.

    Returns:
        List of chord entries from the database.

    Raises:
        FileNotFoundError: If the database file doesn't exist.
        IOError: If the database cannot be read or unpickled.
    """
    if not db_path.exists():
        raise FileNotFoundError(f"Chord database not found: {db_path}")

    try:
        with open(db_path, "rb") as infile:
            return pickle.load(infile)
    except pickle.UnpicklingError as e:
        raise OSError(f"Failed to parse chord database: {db_path}") from e
    except Exception as e:
        raise OSError(f"Failed to read chord database: {db_path}") from e


def parse_tab_file(tab_path: Path = ASCII_TAB_PATH) -> tuple[list, list]:
    """
    Parse an ASCII tab file and extract notes and key information.

    Args:
        tab_path: Path to the ASCII tab file.

    Returns:
        Tuple of (key, allNotes) where:
            - key: List of string tunings (uppercase letters)
            - allNotes: List of [string_num, fret_num, position] triplets

    Raises:
        FileNotFoundError: If the tab file doesn't exist.
        IOError: If the tab file cannot be read.
    """
    if not tab_path.exists():
        raise FileNotFoundError(f"Tab file not found: {tab_path}")

    key = []
    all_notes = []
    string_count = 1

    try:
        with open(tab_path) as infile:
            for line in infile:
                if string_count > 6:
                    string_count = 1
                if line and line[0] in ALLOWED_KEY:
                    line_pos = []
                    key.append(line[0].upper())
                    line_notes = line.replace('|', ' ').replace('\\', ' ').split('-')
                    count = 0
                    for note in line_notes:
                        count += 1
                        if note.isdigit():
                            line_pos.append(count)
                    line_notes = [int(x) for x in line_notes if x.isdigit()]
                    for i in range(len(line_notes)):
                        all_notes.append([string_count, line_notes[i], line_pos[i]])
                    string_count += 1
    except Exception as e:
        raise OSError(f"Failed to read tab file: {tab_path}") from e

    all_notes = sorted(all_notes, key=itemgetter(2))

    if not key:
        raise ValueError(f"No valid tab lines found in file: {tab_path}")

    if len(key) > 6:
        raise ValueError(
            f"Tab file contains more than 6 strings ({len(key)} found). "
            "Only standard 6-string guitar tabs are supported."
        )

    return key, all_notes


def chord_recognition(key: list, chord_notes: list, chord_db: list) -> None:
    """
    Run the set of notes for a single chord against the database to find matches.

    Args:
        key: List of string tunings.
        chord_notes: List of [string_num, fret_num, position] triplets for the chord.
        chord_db: The chord database loaded from pickle file.
    """
    chord = ''
    i = len(chord_notes) - 1
    while i >= 0:
        chord += key[chord_notes[i][0] - 1] + ' ' + str(chord_notes[i][1]) + ' '
        i -= 1

    chord_set = [x[1] for x in chord_db]
    if chord in chord_set:
        index = chord_set.index(chord)
        chord_name = chord_db[index][0]
        print("Chord recognized -", chord_name)
        for i in range(len(chord_db)):
            if chord_db[i][0] == chord_name:
                print("Alternate fingering -", chord_db[i][1])


def find_and_recognize_chords(key: list, all_notes: list, chord_db: list) -> None:
    """
    Find chords in the note list and recognize them using the database.

    Chords are identified by checking successive notes to see if notes from
    different strings are equidistant from the left (played at the same time).

    Args:
        key: List of string tunings.
        all_notes: Sorted list of [string_num, fret_num, position] triplets.
        chord_db: The chord database loaded from pickle file.
    """
    chord_notes = []
    i = 0
    while i < len(all_notes) - 1:
        x = all_notes[i]
        y = all_notes[i + 1]
        if x[2] == y[2]:
            chord_notes.append(x)
            chord_notes.append(y)
            i += 1
            if i < len(all_notes) - 1:
                y = all_notes[i + 1]
            while x[2] == y[2] and i < len(all_notes) - 1:
                chord_notes.append(y)
                i += 1
                if i < len(all_notes) - 1:
                    y = all_notes[i + 1]
        chord_recognition(key, chord_notes, chord_db)
        i += 1
        chord_notes = []


def main():
    """Main entry point when running as a script."""
    try:
        chord_db = load_chord_database()
    except (OSError, FileNotFoundError) as e:
        print(f"Error loading chord database: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        key, all_notes = parse_tab_file()
    except (OSError, FileNotFoundError, ValueError) as e:
        print(f"Error loading tab file: {e}", file=sys.stderr)
        sys.exit(1)

    find_and_recognize_chords(key, all_notes, chord_db)


if __name__ == "__main__":
    main()
