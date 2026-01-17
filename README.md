# OCR-tabber

An app that scans input images containing guitar tabs and converts them to ASCII text format, with automatic chord recognition.

## Features

- **OCR Processing**: Convert guitar tab images to ASCII text using Tesseract OCR
- **Chord Recognition**: Automatically identify chords in ASCII tabs from a comprehensive database
- **Modern Python 3**: Fully upgraded to Python 3.9+ with type hints and modern best practices
- **Isolated Environment**: Uses modern build system (pyproject.toml) to avoid polluting your system Python

## Requirements

- **Python 3.9 or higher**
- **Tesseract OCR** (system dependency)

### Install Tesseract OCR

```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract

# Windows
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
```

## Installation

### Option 1: Install in Development Mode (Recommended)

```bash
# Clone the repository
git clone https://github.com/sn0v/OCR-tabber.git
cd OCR-tabber

# Create a virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in editable mode with development dependencies
pip install -e .[dev]
```

### Option 2: Install as a Package

```bash
pip install git+https://github.com/sn0v/OCR-tabber.git
```

## Usage

After installation, three command-line tools are available:

### 1. OCR Tab Image to ASCII

```bash
ocr-tab path/to/tab_image.png
```

### 2. Recognize Chords in ASCII Tab

```bash
chord-recognizer path/to/ascii_tab.txt
```

### 3. Extract Chord Database (for developers)

```bash
extract-chord-db data/mainDB.xml data/mainDB.pkl
```

## Development

### Setup Development Environment

```bash
# Install with development dependencies
pip install -e .[dev]

# Run linting and formatting
ruff check src/
ruff format src/

# Run type checking
mypy src/

# Run tests (when test suite is added)
pytest
```

### Project Structure

```
OCR-tabber/
├── src/ocr_tabber/          # Main package
│   ├── ocr_tab.py           # OCR processing module
│   ├── chord_recognizer.py  # Chord recognition module
│   └── tabDBextractor.py    # Database extraction utility
├── data/                     # Chord databases
│   ├── mainDB.xml           # Source XML database (Gnome Guitar)
│   └── mainDB.pkl           # Processed pickle database
├── pyproject.toml           # Modern Python build configuration
└── README.md                # This file
```

## What's New in v2.0

- Migrated from Python 2 to Python 3.9+
- Replaced deprecated `tesseract` module with modern `pytesseract`
- Added proper package structure with entry points
- Implemented modern build system using `pyproject.toml`
- Added type hints and comprehensive documentation
- Fixed performance issues (chord database loaded once, not per-chord)
- Added proper error handling and path management
- Included development tools (ruff, mypy, pytest)
- Uses virtual environments to isolate from system Python

License
=======

This project is licensed under the [Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0.html)

    /*
     * Copyright 2014 Utkarsh Jaiswal
     *
     * Licensed under the Apache License, Version 2.0 (the "License");
     * you may not use this file except in compliance with the License.
     * You may obtain a copy of the License at
     *
     *      http://www.apache.org/licenses/LICENSE-2.0
     *
     * Unless required by applicable law or agreed to in writing, software
     * distributed under the License is distributed on an "AS IS" BASIS,
     * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
     * See the License for the specific language governing permissions and
     * limitations under the License.
     */

The chord database used here (packaged with [Gnome Guitar](http://gnome-chord.sourceforge.net/)) is distributed under the GPL 2.0 license.
