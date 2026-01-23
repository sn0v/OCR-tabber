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
        """Test parsing the default ASCII tab file returns valid structure."""
        key, all_notes = parse_tab_file(data_dir / "ASCIItab.txt")

        # Verify key structure
        assert isinstance(key, list)
        assert len(key) == 6  # 6-string guitar
        for k in key:
            assert k in [x.upper() for x in ALLOWED_KEY]

        # Verify notes structure
        assert isinstance(all_notes, list)
        for note in all_notes:
            assert len(note) == 3
            assert all(isinstance(n, int) for n in note)

    def test_parse_nonexistent_file(self, temp_dir: Path):
        """Test that FileNotFoundError is raised for missing files."""
        with pytest.raises(FileNotFoundError, match="Tab file not found"):
            parse_tab_file(temp_dir / "nonexistent.txt")

    @pytest.mark.parametrize("content", ["", "This is not a tab\nJust some text\n"])
    def test_parse_invalid_content(self, temp_dir: Path, content: str):
        """Test that ValueError is raised for files without valid tab lines."""
        invalid_file = temp_dir / "invalid.txt"
        invalid_file.write_text(content)
        with pytest.raises(ValueError, match="No valid tab lines found"):
            parse_tab_file(invalid_file)

    def test_parse_custom_tab(self, temp_dir: Path, sample_tab_content: str):
        """Test parsing a custom tab file with sorting verification."""
        tab_file = temp_dir / "custom.txt"
        tab_file.write_text(sample_tab_content)

        key, all_notes = parse_tab_file(tab_file)

        assert len(key) == 6
        assert key == ['E', 'B', 'G', 'D', 'A', 'E']
        assert len(all_notes) > 0

        # Verify notes are sorted by position
        positions = [note[2] for note in all_notes]
        assert positions == sorted(positions)


class TestAllowedKey:
    """Tests for the ALLOWED_KEY constant."""

    def test_allowed_key_format(self):
        """Test that ALLOWED_KEY contains all notes in both cases."""
        expected_notes = ['a', 'b', 'c', 'd', 'e', 'f', 'g']
        for note in expected_notes:
            assert note in ALLOWED_KEY
            assert note.upper() in ALLOWED_KEY

        assert len(ALLOWED_KEY) == 14  # 7 notes * 2 cases
