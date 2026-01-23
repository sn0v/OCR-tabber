"""Tests for the chord_recognizer module."""

from pathlib import Path

import pytest

from ocr_tabber.chord_recognizer import (
    ALLOWED_KEY,
    load_chord_database,
    parse_tab_file,
)


class TestLoadChordDatabase:
    """Tests for load_chord_database function."""

    def test_load_main_database(self, data_dir: Path):
        """Test loading the main chord database."""
        result = load_chord_database(data_dir / "mainDB.pkl")
        assert isinstance(result, list)
        assert len(result) > 0
        # Each entry should be [chord_name, chord_frets]
        assert len(result[0]) == 2

    def test_load_nonexistent_file(self, temp_dir: Path):
        """Test that FileNotFoundError is raised for missing files."""
        with pytest.raises(FileNotFoundError, match="Chord database not found"):
            load_chord_database(temp_dir / "nonexistent.pkl")

    def test_load_invalid_pickle(self, temp_dir: Path):
        """Test that IOError is raised for invalid pickle files."""
        invalid_pkl = temp_dir / "invalid.pkl"
        invalid_pkl.write_text("not a pickle file")
        with pytest.raises(IOError, match="Failed to"):
            load_chord_database(invalid_pkl)


class TestParseTabFile:
    """Tests for parse_tab_file function."""

    def test_parse_default_tab_file(self, data_dir: Path):
        """Test parsing the default ASCII tab file."""
        key, all_notes = parse_tab_file(data_dir / "ASCIItab.txt")

        assert isinstance(key, list)
        assert isinstance(all_notes, list)
        assert len(key) == 6  # 6-string guitar
        # All keys should be uppercase letters
        for k in key:
            assert k in [x.upper() for x in ALLOWED_KEY]

    def test_parse_tab_returns_notes(self, data_dir: Path):
        """Test that parsing returns properly formatted notes."""
        key, all_notes = parse_tab_file(data_dir / "ASCIItab.txt")

        # Each note should be [string_num, fret_num, position]
        for note in all_notes:
            assert len(note) == 3
            assert isinstance(note[0], int)  # string number
            assert isinstance(note[1], int)  # fret number
            assert isinstance(note[2], int)  # position

    def test_parse_nonexistent_file(self, temp_dir: Path):
        """Test that FileNotFoundError is raised for missing files."""
        with pytest.raises(FileNotFoundError, match="Tab file not found"):
            parse_tab_file(temp_dir / "nonexistent.txt")

    def test_parse_empty_file(self, temp_dir: Path):
        """Test that ValueError is raised for empty files."""
        empty_file = temp_dir / "empty.txt"
        empty_file.write_text("")
        with pytest.raises(ValueError, match="No valid tab lines found"):
            parse_tab_file(empty_file)

    def test_parse_no_valid_lines(self, temp_dir: Path):
        """Test that ValueError is raised when no valid tab lines exist."""
        invalid_tab = temp_dir / "invalid.txt"
        invalid_tab.write_text("This is not a tab\nJust some text\n")
        with pytest.raises(ValueError, match="No valid tab lines found"):
            parse_tab_file(invalid_tab)

    def test_parse_custom_tab(self, temp_dir: Path, sample_tab_content: str):
        """Test parsing a custom tab file."""
        tab_file = temp_dir / "custom.txt"
        tab_file.write_text(sample_tab_content)

        key, all_notes = parse_tab_file(tab_file)

        assert len(key) == 6
        assert key == ['E', 'B', 'G', 'D', 'A', 'E']
        assert len(all_notes) > 0

    def test_notes_sorted_by_position(self, temp_dir: Path, sample_tab_content: str):
        """Test that notes are sorted by position."""
        tab_file = temp_dir / "sorted.txt"
        tab_file.write_text(sample_tab_content)

        _, all_notes = parse_tab_file(tab_file)

        # Verify notes are sorted by position (index 2)
        positions = [note[2] for note in all_notes]
        assert positions == sorted(positions)


class TestAllowedKey:
    """Tests for the ALLOWED_KEY constant."""

    def test_allowed_key_contains_notes(self):
        """Test that ALLOWED_KEY contains all guitar string notes."""
        expected_notes = ['a', 'b', 'c', 'd', 'e', 'f', 'g']
        for note in expected_notes:
            assert note in ALLOWED_KEY
            assert note.upper() in ALLOWED_KEY

    def test_allowed_key_length(self):
        """Test that ALLOWED_KEY has correct length (7 notes * 2 cases)."""
        assert len(ALLOWED_KEY) == 14
