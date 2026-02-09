"""Tests for the formatters module."""

import csv
import io
import json

import pytest

from ocr_tabber.chord_recognizer import ChordResult
from ocr_tabber.formatters import (
    FORMATS,
    format_csv,
    format_json,
    format_ocr_csv,
    format_ocr_json,
    format_ocr_text,
    format_text,
    get_formatter,
    get_ocr_formatter,
)


@pytest.fixture
def single_chord() -> list[ChordResult]:
    """A single recognized chord with two fingerings."""
    return [
        {
            "chord_name": "A Major",
            "fingerings": ["A 0 D 2 G 2 B 2 E 0 ", "A 0 D 2 G 2 B 2 E 5 "],
        }
    ]


@pytest.fixture
def multiple_chords() -> list[ChordResult]:
    """Multiple recognized chords."""
    return [
        {
            "chord_name": "A Major",
            "fingerings": ["A 0 D 2 G 2 B 2 E 0 "],
        },
        {
            "chord_name": "G Major",
            "fingerings": ["E 3 A 2 D 0 G 0 B 0 E 3 "],
        },
    ]


@pytest.fixture
def empty_results() -> list[ChordResult]:
    """No recognized chords."""
    return []


class TestFormatText:
    """Tests for the text formatter."""

    def test_single_chord(self, single_chord: list[ChordResult]):
        """Test text output for a single chord with multiple fingerings."""
        result = format_text(single_chord)
        lines = result.split("\n")
        assert lines[0] == "Chord recognized - A Major"
        assert lines[1] == "Alternate fingering - A 0 D 2 G 2 B 2 E 0 "
        assert lines[2] == "Alternate fingering - A 0 D 2 G 2 B 2 E 5 "

    def test_multiple_chords(self, multiple_chords: list[ChordResult]):
        """Test text output for multiple chords."""
        result = format_text(multiple_chords)
        assert "Chord recognized - A Major" in result
        assert "Chord recognized - G Major" in result

    def test_empty_results(self, empty_results: list[ChordResult]):
        """Test text output with no chords."""
        result = format_text(empty_results)
        assert result == ""


class TestFormatJson:
    """Tests for the JSON formatter."""

    def test_single_chord(self, single_chord: list[ChordResult]):
        """Test JSON output for a single chord."""
        result = format_json(single_chord)
        parsed = json.loads(result)
        assert isinstance(parsed, list)
        assert len(parsed) == 1
        assert parsed[0]["chord_name"] == "A Major"
        assert len(parsed[0]["fingerings"]) == 2

    def test_multiple_chords(self, multiple_chords: list[ChordResult]):
        """Test JSON output for multiple chords."""
        result = format_json(multiple_chords)
        parsed = json.loads(result)
        assert len(parsed) == 2
        assert parsed[0]["chord_name"] == "A Major"
        assert parsed[1]["chord_name"] == "G Major"

    def test_empty_results(self, empty_results: list[ChordResult]):
        """Test JSON output with no chords."""
        result = format_json(empty_results)
        parsed = json.loads(result)
        assert parsed == []

    def test_valid_json(self, single_chord: list[ChordResult]):
        """Test that output is valid JSON."""
        result = format_json(single_chord)
        # Should not raise
        json.loads(result)


class TestFormatCsv:
    """Tests for the CSV formatter."""

    def test_single_chord(self, single_chord: list[ChordResult]):
        """Test CSV output for a single chord with multiple fingerings."""
        result = format_csv(single_chord)
        reader = csv.reader(io.StringIO(result))
        rows = list(reader)
        assert rows[0] == ["chord_name", "fingering"]
        assert rows[1][0] == "A Major"
        assert rows[2][0] == "A Major"
        assert len(rows) == 3  # header + 2 fingerings

    def test_multiple_chords(self, multiple_chords: list[ChordResult]):
        """Test CSV output for multiple chords."""
        result = format_csv(multiple_chords)
        reader = csv.reader(io.StringIO(result))
        rows = list(reader)
        assert rows[0] == ["chord_name", "fingering"]
        assert len(rows) == 3  # header + 1 + 1

    def test_empty_results(self, empty_results: list[ChordResult]):
        """Test CSV output with no chords."""
        result = format_csv(empty_results)
        reader = csv.reader(io.StringIO(result))
        rows = list(reader)
        assert rows == [["chord_name", "fingering"]]

    def test_valid_csv(self, single_chord: list[ChordResult]):
        """Test that output is valid CSV."""
        result = format_csv(single_chord)
        reader = csv.reader(io.StringIO(result))
        # Should not raise
        list(reader)


class TestFormatOcrText:
    """Tests for the OCR text formatter."""

    def test_passthrough(self):
        """Test that text format returns OCR result unchanged."""
        ocr_text = "e|--0--\nB|--1--"
        assert format_ocr_text(ocr_text) == ocr_text

    def test_empty_string(self):
        """Test with empty OCR result."""
        assert format_ocr_text("") == ""


class TestFormatOcrJson:
    """Tests for the OCR JSON formatter."""

    def test_wraps_in_object(self):
        """Test that OCR text is wrapped in a JSON object."""
        ocr_text = "e|--0--\nB|--1--"
        result = format_ocr_json(ocr_text)
        parsed = json.loads(result)
        assert parsed["ocr_text"] == ocr_text

    def test_empty_string(self):
        """Test with empty OCR result."""
        result = format_ocr_json("")
        parsed = json.loads(result)
        assert parsed["ocr_text"] == ""


class TestFormatOcrCsv:
    """Tests for the OCR CSV formatter."""

    def test_lines_as_rows(self):
        """Test that each OCR line becomes a CSV row."""
        ocr_text = "e|--0--\nB|--1--"
        result = format_ocr_csv(ocr_text)
        reader = csv.reader(io.StringIO(result))
        rows = list(reader)
        assert rows[0] == ["line"]
        assert rows[1] == ["e|--0--"]
        assert rows[2] == ["B|--1--"]

    def test_empty_string(self):
        """Test with empty OCR result."""
        result = format_ocr_csv("")
        reader = csv.reader(io.StringIO(result))
        rows = list(reader)
        assert rows == [["line"]]


class TestGetFormatter:
    """Tests for the get_formatter function."""

    @pytest.mark.parametrize("fmt", ["text", "json", "csv"])
    def test_valid_formats(self, fmt: str):
        """Test that all valid format names return a callable."""
        formatter = get_formatter(fmt)
        assert callable(formatter)

    def test_invalid_format(self):
        """Test that an invalid format raises ValueError."""
        with pytest.raises(ValueError, match="Unknown format"):
            get_formatter("xml")


class TestGetOcrFormatter:
    """Tests for the get_ocr_formatter function."""

    @pytest.mark.parametrize("fmt", ["text", "json", "csv"])
    def test_valid_formats(self, fmt: str):
        """Test that all valid format names return a callable."""
        formatter = get_ocr_formatter(fmt)
        assert callable(formatter)

    def test_invalid_format(self):
        """Test that an invalid format raises ValueError."""
        with pytest.raises(ValueError, match="Unknown format"):
            get_ocr_formatter("yaml")


class TestFormats:
    """Tests for the FORMATS constant."""

    def test_contains_expected_formats(self):
        """Test that FORMATS contains all expected format names."""
        assert "text" in FORMATS
        assert "json" in FORMATS
        assert "csv" in FORMATS

    def test_format_count(self):
        """Test that FORMATS has exactly 3 entries."""
        assert len(FORMATS) == 3
