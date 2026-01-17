#!/usr/bin/env python3
# Copyright 2014 Utkarsh Jaiswal
# Updated 2026 - Modernized for Python 3

"""
Utility script to parse the XML chord database packaged with Gnome Guitar.
Extracts relevant info (chord names, fret positions) while leaving out the rest.
Fret positions are always extracted from thickest to thinnest string (EADGBE for standard E tuning).

Source: http://gnome-chord.sourceforge.net/
"""

import pickle
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Tuple


def parse_chord_database(xml_path: Path) -> List[Tuple[str, str]]:
    """
    Parse XML chord database and extract chord names and fret positions.

    Args:
        xml_path: Path to the XML chord database file

    Returns:
        List of (chord_name, chord_frets) tuples where:
        - chord_name: Name of the chord (e.g., "C", "Am", "G7")
        - chord_frets: String representation of fret positions
          (e.g., "E None A 3 D 2 G 0 B 1 E 0" for C major)

    Raises:
        FileNotFoundError: If the XML file doesn't exist
        ET.ParseError: If the XML is malformed
    """
    if not xml_path.exists():
        raise FileNotFoundError(f"Database file not found: {xml_path}")

    tree = ET.parse(xml_path)
    root = tree.getroot()

    # A list is used instead of dict since database contains
    # multiple fingerings for each chord (not unique keys)
    chord_list = []

    for child in root:  # Each child is a chord element
        chord_name = child.attrib.get("name", "Unknown")

        # Build fret data string for current chord
        # Format: "string_note fret_number string_note fret_number ..."
        # Example: "E None A 3 D 2 G 0 B 1 E 0" for C major
        chord_frets = ""

        for g_str in child.findall("./voiceing/guitarString"):
            # g_str[0] = string tuning (note)
            # g_str[2] = fret number
            if len(g_str) > 2 and g_str[2].text:
                chord_frets += f"{g_str[0].text} {g_str[2].text} "

        if chord_frets:  # Only add if we found fret data
            chord_list.append([chord_name, chord_frets])

    return chord_list


def save_chord_database(chord_list: List[Tuple[str, str]], output_path: Path) -> None:
    """
    Save chord list to a pickle file for fast loading.

    Args:
        chord_list: List of (chord_name, chord_frets) tuples
        output_path: Path where the pickle file should be saved
    """
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "wb") as outfile:
        pickle.dump(chord_list, outfile)


def main() -> int:
    """
    Main entry point for the extract-chord-db command-line tool.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    # Default paths relative to package structure
    default_input = Path(__file__).parent.parent.parent / "data" / "mainDB.xml"
    default_output = Path(__file__).parent.parent.parent / "data" / "mainDB.pkl"

    if len(sys.argv) > 1:
        input_path = Path(sys.argv[1])
    else:
        input_path = default_input

    if len(sys.argv) > 2:
        output_path = Path(sys.argv[2])
    else:
        output_path = default_output

    try:
        print(f"Parsing XML database: {input_path}")
        chord_list = parse_chord_database(input_path)

        print(f"Extracted {len(chord_list)} chord fingerings")

        print(f"Saving to: {output_path}")
        save_chord_database(chord_list, output_path)

        print("Chord database extraction complete!")
        return 0

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        print(
            "\nUsage: extract-chord-db [input_xml] [output_pkl]", file=sys.stderr
        )
        print(f"Default input: {default_input}", file=sys.stderr)
        print(f"Default output: {default_output}", file=sys.stderr)
        return 1
    except ET.ParseError as e:
        print(f"XML parsing error: {e}", file=sys.stderr)
        print("Make sure the input file is valid XML", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
