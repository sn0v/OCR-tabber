"""Output formatters for OCR and chord recognition results."""

import csv
import io
import json
from collections.abc import Callable

from ocr_tabber.chord_recognizer import ChordResult

# Supported output format names
FORMATS = ("text", "json", "csv")


def format_text(results: list[ChordResult]) -> str:
    """
    Format chord results as plain text.

    Produces the same output as the original print-based chord_recognition,
    with each chord name followed by its alternate fingerings.

    Args:
        results: List of ChordResult dicts from find_and_recognize_chords.

    Returns:
        Formatted plain text string.
    """
    lines: list[str] = []
    for result in results:
        lines.append(f"Chord recognized - {result['chord_name']}")
        for fingering in result["fingerings"]:
            lines.append(f"Alternate fingering - {fingering}")
    return "\n".join(lines)


def format_json(results: list[ChordResult]) -> str:
    """
    Format chord results as JSON.

    Args:
        results: List of ChordResult dicts from find_and_recognize_chords.

    Returns:
        JSON string with an array of chord objects.
    """
    return json.dumps(results, indent=2)


def format_csv(results: list[ChordResult]) -> str:
    """
    Format chord results as CSV.

    Each row contains a chord name and one fingering. Chords with multiple
    fingerings produce multiple rows.

    Args:
        results: List of ChordResult dicts from find_and_recognize_chords.

    Returns:
        CSV string with header row.
    """
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["chord_name", "fingering"])
    for result in results:
        for fingering in result["fingerings"]:
            writer.writerow([result["chord_name"], fingering])
    return output.getvalue().rstrip("\n")


def format_ocr_text(ocr_result: str) -> str:
    """
    Format OCR result as plain text (passthrough).

    Args:
        ocr_result: Raw OCR text string.

    Returns:
        The OCR text unchanged.
    """
    return ocr_result


def format_ocr_json(ocr_result: str) -> str:
    """
    Format OCR result as JSON.

    Args:
        ocr_result: Raw OCR text string.

    Returns:
        JSON string with an ocr_text field.
    """
    return json.dumps({"ocr_text": ocr_result}, indent=2)


def format_ocr_csv(ocr_result: str) -> str:
    """
    Format OCR result as CSV.

    Each line of the OCR output becomes a row.

    Args:
        ocr_result: Raw OCR text string.

    Returns:
        CSV string with header row.
    """
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["line"])
    for line in ocr_result.splitlines():
        writer.writerow([line])
    return output.getvalue().rstrip("\n")


def get_formatter(fmt: str) -> Callable[[list[ChordResult]], str]:
    """
    Get a chord recognition formatter function by name.

    Args:
        fmt: Format name - one of "text", "json", or "csv".

    Returns:
        A formatter function that takes list[ChordResult] and returns str.

    Raises:
        ValueError: If the format name is not recognized.
    """
    formatters: dict[str, Callable[[list[ChordResult]], str]] = {
        "text": format_text,
        "json": format_json,
        "csv": format_csv,
    }
    if fmt not in formatters:
        raise ValueError(f"Unknown format: {fmt!r}. Supported formats: {', '.join(FORMATS)}")
    return formatters[fmt]


def get_ocr_formatter(fmt: str) -> Callable[[str], str]:
    """
    Get an OCR output formatter function by name.

    Args:
        fmt: Format name - one of "text", "json", or "csv".

    Returns:
        A formatter function that takes an OCR text string and returns str.

    Raises:
        ValueError: If the format name is not recognized.
    """
    formatters: dict[str, Callable[[str], str]] = {
        "text": format_ocr_text,
        "json": format_ocr_json,
        "csv": format_ocr_csv,
    }
    if fmt not in formatters:
        raise ValueError(f"Unknown format: {fmt!r}. Supported formats: {', '.join(FORMATS)}")
    return formatters[fmt]
