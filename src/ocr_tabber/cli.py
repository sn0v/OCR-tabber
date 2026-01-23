"""Command-line interface for OCR-tabber."""

import argparse
import sys
from pathlib import Path

from ocr_tabber.chord_recognizer import (
    ASCII_TAB_PATH,
    find_and_recognize_chords,
    load_chord_database,
    parse_tab_file,
)
from ocr_tabber.ocr_tab import ocr_tab_image
from ocr_tabber.tab_db_extractor import (
    OUTPUT_DB_PATH,
    parse_xml_database,
    save_pickle_database,
)


def cmd_ocr(args: argparse.Namespace) -> int:
    """Run OCR on a guitar tab image."""
    try:
        result = ocr_tab_image(args.image)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except (OSError, RuntimeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    if args.output:
        try:
            Path(args.output).write_text(result)
            print(f"Output written to {args.output}")
        except OSError as e:
            print(f"Error writing output: {e}", file=sys.stderr)
            return 1
    else:
        print(result)

    return 0


def cmd_recognize(args: argparse.Namespace) -> int:
    """Recognize chords from an ASCII tab file."""
    tab_path = Path(args.tab_file) if args.tab_file else ASCII_TAB_PATH

    try:
        chord_db = load_chord_database()
    except (OSError, FileNotFoundError) as e:
        print(f"Error loading chord database: {e}", file=sys.stderr)
        return 1

    try:
        key, all_notes = parse_tab_file(tab_path)
    except (OSError, FileNotFoundError, ValueError) as e:
        print(f"Error loading tab file: {e}", file=sys.stderr)
        return 1

    find_and_recognize_chords(key, all_notes, chord_db)
    return 0


def cmd_build_db(args: argparse.Namespace) -> int:
    """Build the chord database from XML source."""
    try:
        chord_list = parse_xml_database()
    except (OSError, FileNotFoundError, ValueError) as e:
        print(f"Error reading XML database: {e}", file=sys.stderr)
        return 1

    try:
        save_pickle_database(chord_list)
    except OSError as e:
        print(f"Error writing pickle database: {e}", file=sys.stderr)
        return 1

    print(f"Successfully extracted {len(chord_list)} chords to {OUTPUT_DB_PATH}")
    return 0


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog="ocr-tabber",
        description="OCR tool for guitar tablature recognition",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0",
    )

    subparsers = parser.add_subparsers(
        title="commands",
        dest="command",
        required=True,
    )

    # ocr command
    ocr_parser = subparsers.add_parser(
        "ocr",
        help="Extract text from a guitar tab image",
    )
    ocr_parser.add_argument(
        "image",
        help="Path to the image file containing guitar tablature",
    )
    ocr_parser.add_argument(
        "-o", "--output",
        help="Write output to file instead of stdout",
    )
    ocr_parser.set_defaults(func=cmd_ocr)

    # recognize command
    recognize_parser = subparsers.add_parser(
        "recognize",
        help="Recognize chords from an ASCII tab file",
    )
    recognize_parser.add_argument(
        "-t", "--tab-file",
        help=f"Path to ASCII tab file (default: {ASCII_TAB_PATH})",
    )
    recognize_parser.set_defaults(func=cmd_recognize)

    # build-db command
    build_db_parser = subparsers.add_parser(
        "build-db",
        help="Rebuild the chord database from XML source",
    )
    build_db_parser.set_defaults(func=cmd_build_db)

    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point for the ocr-tabber command."""
    parser = create_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
