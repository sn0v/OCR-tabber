"""Tests for the tab_db_extractor module."""

import pickle
from pathlib import Path

import pytest

from ocr_tabber.tab_db_extractor import parse_xml_database, save_pickle_database


class TestParseXmlDatabase:
    """Tests for parse_xml_database function."""

    def test_parse_valid_xml(self, data_dir: Path):
        """Test parsing the main XML database."""
        result = parse_xml_database(data_dir / "mainDB.xml")
        assert isinstance(result, list)
        assert len(result) > 0
        # Each entry should be [chord_name, chord_frets]
        assert len(result[0]) == 2
        assert isinstance(result[0][0], str)  # chord name
        assert isinstance(result[0][1], str)  # chord frets

    def test_parse_test_xml(self, data_dir: Path):
        """Test parsing the test XML database."""
        result = parse_xml_database(data_dir / "testDB.xml")
        assert isinstance(result, list)
        assert len(result) == 2  # testDB.xml has A Major and C Major
        chord_names = [entry[0] for entry in result]
        assert "A Major" in chord_names
        assert "C Major" in chord_names

    def test_parse_nonexistent_file(self, temp_dir: Path):
        """Test that FileNotFoundError is raised for missing files."""
        with pytest.raises(FileNotFoundError, match="XML database not found"):
            parse_xml_database(temp_dir / "nonexistent.xml")

    def test_parse_invalid_xml(self, temp_dir: Path):
        """Test that IOError is raised for invalid XML."""
        invalid_xml = temp_dir / "invalid.xml"
        invalid_xml.write_text("not valid xml <unclosed")
        with pytest.raises(IOError, match="Failed to parse XML database"):
            parse_xml_database(invalid_xml)

    def test_parse_wrong_root_element(self, temp_dir: Path):
        """Test that ValueError is raised for wrong root element."""
        wrong_root = temp_dir / "wrong_root.xml"
        wrong_root.write_text('<?xml version="1.0"?><wrong_root></wrong_root>')
        with pytest.raises(ValueError, match="expected root element 'chords'"):
            parse_xml_database(wrong_root)

    def test_parse_missing_name_attribute(self, temp_dir: Path):
        """Test that ValueError is raised when chord is missing name attribute."""
        missing_name = temp_dir / "missing_name.xml"
        missing_name.write_text('<?xml version="1.0"?><chords><chord></chord></chords>')
        with pytest.raises(ValueError, match="missing 'name' attribute"):
            parse_xml_database(missing_name)

    def test_parse_empty_database(self, temp_dir: Path):
        """Test that ValueError is raised for empty database."""
        empty_db = temp_dir / "empty.xml"
        empty_db.write_text('<?xml version="1.0"?><chords></chords>')
        with pytest.raises(ValueError, match="No chord entries found"):
            parse_xml_database(empty_db)


class TestSavePickleDatabase:
    """Tests for save_pickle_database function."""

    def test_save_and_load(self, temp_dir: Path):
        """Test saving and loading a pickle database."""
        chord_list = [["A Major", "A 0 D 2 G 2 B 2 E 0 "], ["C Major", "A 3 D 2 G 0 B 1 E 0 "]]
        output_path = temp_dir / "test.pkl"

        save_pickle_database(chord_list, output_path)

        assert output_path.exists()
        with open(output_path, "rb") as f:
            loaded = pickle.load(f)
        assert loaded == chord_list

    def test_save_to_invalid_path(self, temp_dir: Path):
        """Test that IOError is raised when writing to invalid path."""
        chord_list = [["A Major", "A 0 "]]
        invalid_path = temp_dir / "nonexistent_dir" / "test.pkl"

        with pytest.raises(IOError, match="Failed to write pickle database"):
            save_pickle_database(chord_list, invalid_path)
