"""Command-line interface for OCR-tabber."""

import argparse
import sys
import tempfile
from pathlib import Path

from ocr_tabber.chord_recognizer import (
    ASCII_TAB_PATH,
    find_and_recognize_chords,
    load_chord_database,
    parse_tab_file,
)
from ocr_tabber.formatters import FORMATS, get_formatter, get_ocr_formatter
from ocr_tabber.ocr_tab import batch_ocr_images, ocr_tab_image
from ocr_tabber.tab_db_extractor import (
    OUTPUT_DB_PATH,
    parse_xml_database,
    save_json_database,
)


def cmd_ocr(args: argparse.Namespace) -> int:
    """Run OCR on a guitar tab image."""
    try:
        result = ocr_tab_image(args.image, preprocess=not args.no_preprocess)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except (OSError, RuntimeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    formatter = get_ocr_formatter(args.format)
    output = formatter(result)
    return _write_output(output, args.output)


def _write_output(text: str, output_path: str | None) -> int:
    """
    Write formatted output to a file or stdout.

    Args:
        text: The formatted text to output.
        output_path: File path to write to, or None for stdout.

    Returns:
        0 on success, 1 on error.
    """
    if output_path:
        try:
            Path(output_path).write_text(text + "\n")
            print(f"Output written to {output_path}")
        except OSError as e:
            print(f"Error writing output: {e}", file=sys.stderr)
            return 1
    else:
        print(text)
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

    results = find_and_recognize_chords(key, all_notes, chord_db)
    formatter = get_formatter(args.format)
    output = formatter(results)
    return _write_output(output, args.output)


def cmd_batch(args: argparse.Namespace) -> int:
    """Batch process multiple images through the OCR pipeline."""
    sources: list[str] = args.inputs
    output_dir: Path | None = Path(args.output_dir) if args.output_dir else None
    recognize: bool = args.recognize

    # Validate output directory if specified
    if output_dir is not None:
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            print(f"Error creating output directory: {e}", file=sys.stderr)
            return 1

    # Load chord database if recognition is requested
    chord_db = None
    if recognize:
        try:
            chord_db = load_chord_database()
        except (OSError, FileNotFoundError) as e:
            print(f"Error loading chord database: {e}", file=sys.stderr)
            return 1

    # Run batch OCR
    results = batch_ocr_images(sources)

    if not results:
        print("No files to process.", file=sys.stderr)
        return 1

    # Track summary counts
    success_count = 0
    error_count = 0

    for entry in results:
        file_path = entry['file']
        ocr_result = entry['result']
        error = entry['error']

        if error is not None:
            print(f"[FAIL] {file_path}: {error}", file=sys.stderr)
            error_count += 1
            continue

        success_count += 1
        print(f"[OK]   {file_path}")

        # Write result to output file if output directory is specified
        if output_dir is not None and ocr_result is not None:
            out_name = Path(file_path).stem + ".txt"
            out_path = output_dir / out_name
            try:
                out_path.write_text(ocr_result)
                print(f"       -> {out_path}")
            except OSError as e:
                print(f"       -> Error writing output: {e}", file=sys.stderr)
                error_count += 1
                success_count -= 1

        # Run chord recognition if requested
        if recognize and chord_db is not None and ocr_result is not None:
            # Write OCR result to a temp file for parsing
            with tempfile.NamedTemporaryFile(
                mode='w', suffix='.txt', delete=False
            ) as tmp:
                tmp.write(ocr_result)
                tmp_path = Path(tmp.name)

            try:
                key, all_notes = parse_tab_file(tmp_path)
                chord_results = find_and_recognize_chords(key, all_notes, chord_db)
                if chord_results:
                    formatter = get_formatter("text")
                    print(f"       Chords for {Path(file_path).name}:")
                    for line in formatter(chord_results).splitlines():
                        print(f"       {line}")
            except (OSError, FileNotFoundError, ValueError) as e:
                print(
                    f"       Chord recognition failed for {file_path}: {e}",
                    file=sys.stderr,
                )
            finally:
                tmp_path.unlink(missing_ok=True)

    # Print summary
    total = success_count + error_count
    print(f"\nBatch complete: {success_count}/{total} succeeded, {error_count}/{total} failed")

    return 0 if error_count == 0 else 1


def cmd_build_db(args: argparse.Namespace) -> int:
    """Build the chord database from XML source."""
    try:
        chord_list = parse_xml_database()
    except (OSError, FileNotFoundError, ValueError) as e:
        print(f"Error reading XML database: {e}", file=sys.stderr)
        return 1

    try:
        save_json_database(chord_list)
    except OSError as e:
        print(f"Error writing JSON database: {e}", file=sys.stderr)
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
    ocr_parser.add_argument(
        "-f", "--format",
        choices=FORMATS,
        default="text",
        help="Output format (default: text)",
    )
    ocr_parser.add_argument(
        "--no-preprocess",
        action="store_true",
        default=False,
        help="Skip image preprocessing before OCR",
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
    recognize_parser.add_argument(
        "-f", "--format",
        choices=FORMATS,
        default="text",
        help="Output format (default: text)",
    )
    recognize_parser.add_argument(
        "-o", "--output",
        help="Write output to file instead of stdout",
    )
    recognize_parser.set_defaults(func=cmd_recognize)

    # batch command
    batch_parser = subparsers.add_parser(
        "batch",
        help="Batch process multiple tab images through OCR",
    )
    batch_parser.add_argument(
        "inputs",
        nargs="+",
        help=(
            "One or more image files, directories, or glob patterns to process. "
            "Directories are scanned for supported image files."
        ),
    )
    batch_parser.add_argument(
        "-o", "--output-dir",
        help="Directory to save individual OCR result files (one .txt per image)",
    )
    batch_parser.add_argument(
        "-r", "--recognize",
        action="store_true",
        help="Also run chord recognition on each OCR result",
    )
    batch_parser.set_defaults(func=cmd_batch)

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
