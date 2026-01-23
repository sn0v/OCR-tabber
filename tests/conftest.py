"""Shared test fixtures for OCR-tabber tests."""

import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def data_dir() -> Path:
    """Return the path to the data directory."""
    return Path(__file__).parent.parent / "data"


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_tab_content() -> str:
    """Return sample ASCII tab content for testing."""
    return """e|-3---6---3---2-|
B|-3---8---4---3-|
G|-3---8---5---2-|
D|-5---8---5---0-|
A|-5---6---3--- -|
E|- --- --- --- -|
"""


@pytest.fixture
def sample_xml_content() -> str:
    """Return sample XML chord database content for testing."""
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<chords version="1.0">
<chord name="A Major">
<type>major</type>
<root>A</root>
<voiceing>
    <tuning>E,A,D,G,B,E</tuning>
    <guitarString>
        <tuned>E</tuned>
        <fretted></fretted>
        <fretNo></fretNo>
    </guitarString>
    <guitarString>
        <tuned>A</tuned>
        <fretted>A</fretted>
        <fretNo>0</fretNo>
    </guitarString>
    <guitarString>
        <tuned>D</tuned>
        <fretted>E</fretted>
        <fretNo>2</fretNo>
    </guitarString>
    <guitarString>
        <tuned>G</tuned>
        <fretted>A</fretted>
        <fretNo>2</fretNo>
    </guitarString>
    <guitarString>
        <tuned>B</tuned>
        <fretted>C#</fretted>
        <fretNo>2</fretNo>
    </guitarString>
    <guitarString>
        <tuned>E</tuned>
        <fretted>E</fretted>
        <fretNo>0</fretNo>
    </guitarString>
</voiceing>
</chord>
</chords>
"""
