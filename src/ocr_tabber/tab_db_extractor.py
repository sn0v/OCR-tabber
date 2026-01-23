# Copyright 2014 Utkarsh Jaiswal

# Utility script to parse the XML chord database packaged with Gnome Guitar
# (http://gnome-chord.sourceforge.net/)
# It extracts relevant info (chord names, fret positions) while leaving out the rest
# Fret positions are always extracted from thickest to thinnest string
# (EADGBE for standard E tuning)

import pickle
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


# Get the data directory path relative to this module
DATA_DIR = Path(__file__).parent.parent.parent / "data"
INPUT_DB_PATH = DATA_DIR / "mainDB.xml"
OUTPUT_DB_PATH = DATA_DIR / "mainDB.pkl"


def parse_xml_database(xml_path: Path = INPUT_DB_PATH) -> list:
    """
    Parse the XML chord database and extract chord information.

    Args:
        xml_path: Path to the input XML database file.

    Returns:
        List of [chord_name, chord_frets] pairs.

    Raises:
        FileNotFoundError: If the XML file doesn't exist.
        IOError: If the XML file cannot be read or parsed.
    """
    if not xml_path.exists():
        raise FileNotFoundError(f"XML database not found: {xml_path}")

    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
    except ET.ParseError as e:
        raise IOError(f"Failed to parse XML database: {xml_path}") from e
    except Exception as e:
        raise IOError(f"Failed to read XML database: {xml_path}") from e

    # A list is used here since the database contains multiple fingerings for each chord
    chord_list = []

    for child in root:
        chord_name = child.attrib['name']

        # Build chord fret notation as a string with whitespaces
        # Eg - The C major chord will be denoted as 'E None A 3 D 2 G 0 B 1 E 0'
        chord_frets = ''
        for g_str in child.findall('./voiceing/guitarString'):
            if g_str[2].text:
                chord_frets += str(g_str[0].text) + ' ' + str(g_str[2].text) + ' '

        chord_list.append([chord_name, chord_frets])

    return chord_list


def save_pickle_database(chord_list: list, output_path: Path = OUTPUT_DB_PATH) -> None:
    """
    Save the chord list to a pickle file.

    Args:
        chord_list: List of [chord_name, chord_frets] pairs.
        output_path: Path to the output pickle file.

    Raises:
        IOError: If the pickle file cannot be written.
    """
    try:
        with open(output_path, 'wb') as outfile:
            pickle.dump(chord_list, outfile)
    except Exception as e:
        raise IOError(f"Failed to write pickle database: {output_path}") from e


def main():
    """Main entry point when running as a script."""
    try:
        chord_list = parse_xml_database()
    except (FileNotFoundError, IOError) as e:
        print(f"Error reading XML database: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        save_pickle_database(chord_list)
    except IOError as e:
        print(f"Error writing pickle database: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Successfully extracted {len(chord_list)} chords to {OUTPUT_DB_PATH}")


if __name__ == "__main__":
    main()
