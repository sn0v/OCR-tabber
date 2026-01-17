# Desktop App Development Plan: OCR-Tabber

## Executive Summary

Transform OCR-Tabber from a Python 2 CLI proof-of-concept into a polished cross-platform desktop application for Mac, Windows, and Linux. Users will be able to import images of handwritten guitar tabs and convert them to digital formats (ASCII, Guitar Pro, MusicXML).

---

## Phase 1: Foundation & Modernization

### Step 1.1: Python 3 Migration

**Goal:** Update all code to Python 3.11+

**Tasks:**
- [ ] Update print statements: `print "text"` → `print("text")`
- [ ] Replace deprecated `tesseract` module with `pytesseract`
- [ ] Update pickle protocol for Python 3 compatibility
- [ ] Fix any Python 2/3 string encoding differences
- [ ] Add type hints throughout codebase

**Files to modify:**
- `src/ocr-tab.py` (33 lines)
- `src/chord-recognizer.py` (84 lines)
- `src/tabDBextractor.py` (40 lines)

### Step 1.2: Project Structure Modernization

**Goal:** Create a proper Python package structure

**New structure:**
```
OCR-tabber/
├── pyproject.toml              # Modern Python project config
├── requirements.txt            # Dependencies
├── README.md
├── LICENSE.md
├── .gitignore
│
├── ocr_tabber/                 # Main package
│   ├── __init__.py
│   ├── __main__.py             # Entry point
│   ├── core/
│   │   ├── __init__.py
│   │   ├── ocr_engine.py       # OCR processing
│   │   ├── tab_parser.py       # Tab parsing logic
│   │   ├── chord_recognizer.py # Chord recognition
│   │   └── image_processor.py  # Image preprocessing
│   ├── database/
│   │   ├── __init__.py
│   │   ├── chord_db.py         # Chord database manager
│   │   └── models.py           # Data models
│   ├── export/
│   │   ├── __init__.py
│   │   ├── ascii_export.py     # ASCII tab export
│   │   ├── musicxml_export.py  # MusicXML export
│   │   └── midi_export.py      # MIDI export
│   └── ui/
│       ├── __init__.py
│       ├── main_window.py      # Main application window
│       ├── editor_widget.py    # Tab editor component
│       └── preview_widget.py   # Preview component
│
├── data/
│   ├── chords/
│   │   ├── mainDB.xml
│   │   └── mainDB.json         # Convert to JSON
│   └── tessdata/               # Tesseract models
│
├── resources/
│   ├── icons/                  # App icons
│   ├── themes/                 # UI themes
│   └── fonts/                  # Tab fonts
│
└── tests/
    ├── __init__.py
    ├── test_ocr.py
    ├── test_parser.py
    └── test_chord_recognition.py
```

### Step 1.3: Dependencies Setup

**Create `requirements.txt`:**
```
# Core
pytesseract>=0.3.10
Pillow>=10.0.0
numpy>=1.24.0

# Desktop UI (choose one framework - see Step 2)
PySide6>=6.6.0              # Qt for Python (recommended)
# OR
# customtkinter>=5.2.0      # Modern Tkinter
# OR
# PyGObject>=3.44.0         # GTK4 bindings

# Image processing
opencv-python>=4.8.0
scikit-image>=0.21.0

# Export formats
mido>=1.3.0                 # MIDI export
music21>=9.0.0              # MusicXML export

# Development
pytest>=7.4.0
black>=23.0.0
mypy>=1.5.0

# Packaging
pyinstaller>=6.0.0          # Cross-platform bundling
```

---

## Phase 2: Desktop Framework Selection

### Recommended: PySide6 (Qt for Python)

**Why PySide6:**
- True native look on all platforms
- Excellent image handling (QImage, QPixmap)
- Built-in drag-and-drop support
- Professional quality widgets
- Good documentation
- LGPL license (can distribute commercially)
- Active development by Qt Company

**Alternatives considered:**

| Framework | Pros | Cons |
|-----------|------|------|
| **PySide6/PyQt6** | Native look, powerful, mature | Larger bundle size (~150MB) |
| **Electron + Python** | Web tech, flexible UI | Heavy (300MB+), complex IPC |
| **Tauri + Python** | Lightweight, web UI | Rust knowledge needed |
| **CustomTkinter** | Lightweight, simple | Less polished, fewer widgets |
| **Kivy** | Touch-friendly, mobile | Non-native look |
| **PyGTK** | Native on Linux | Poor Windows support |

### Step 2.1: Basic Application Shell

**Create `ocr_tabber/ui/main_window.py`:**

```python
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QSplitter,
    QMenuBar, QMenu, QStatusBar, QProgressBar
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QPixmap, QImage, QAction, QDragEnterEvent, QDropEvent

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OCR Tabber - Handwritten Tab Converter")
        self.setMinimumSize(1200, 800)
        self.setup_ui()
        self.setup_menu()
        self.setup_drag_drop()

    def setup_ui(self):
        # Central widget with splitter
        splitter = QSplitter(Qt.Horizontal)

        # Left panel: Image input
        self.image_panel = ImageInputPanel()

        # Right panel: Tab output/editor
        self.tab_panel = TabOutputPanel()

        splitter.addWidget(self.image_panel)
        splitter.addWidget(self.tab_panel)
        splitter.setSizes([600, 600])

        self.setCentralWidget(splitter)

        # Status bar with progress
        self.status_bar = QStatusBar()
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
        self.setStatusBar(self.status_bar)
```

### Step 2.2: UI Component Breakdown

**Components to build:**

1. **ImageInputPanel** - Image display with zoom/pan
   - Drag-and-drop zone
   - File browser button
   - Image preview with zoom controls
   - Region selection tool
   - Rotation/deskew controls

2. **TabOutputPanel** - Editable tab display
   - ASCII tab text editor
   - Syntax highlighting for tab notation
   - Chord labels overlay
   - Export buttons

3. **ProcessingControls** - OCR controls
   - "Convert" button
   - Processing options (language, confidence threshold)
   - Progress indicator

4. **ChordPanel** - Chord information sidebar
   - Detected chords list
   - Chord diagrams
   - Alternative fingerings

---

## Phase 3: OCR Engine Enhancement

### Step 3.1: Image Preprocessing Pipeline

**Critical for handwritten tab recognition:**

```python
# ocr_tabber/core/image_processor.py

import cv2
import numpy as np
from PIL import Image

class TabImageProcessor:
    """Preprocess handwritten tab images for better OCR accuracy."""

    def process(self, image: np.ndarray) -> np.ndarray:
        """Full preprocessing pipeline."""
        img = self.convert_to_grayscale(image)
        img = self.remove_noise(img)
        img = self.deskew(img)
        img = self.detect_staff_lines(img)
        img = self.enhance_contrast(img)
        img = self.binarize(img)
        return img

    def deskew(self, image: np.ndarray) -> np.ndarray:
        """Correct rotation of scanned/photographed tabs."""
        coords = np.column_stack(np.where(image > 0))
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = 90 + angle
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        return cv2.warpAffine(image, M, (w, h),
                              flags=cv2.INTER_CUBIC,
                              borderMode=cv2.BORDER_REPLICATE)

    def detect_staff_lines(self, image: np.ndarray) -> dict:
        """Detect the 6 horizontal tab lines."""
        # Use Hough transform to find horizontal lines
        edges = cv2.Canny(image, 50, 150)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180,
                                threshold=100,
                                minLineLength=image.shape[1] * 0.5,
                                maxLineGap=10)
        # Filter for horizontal lines (tab strings)
        horizontal = [l for l in lines if abs(l[0][1] - l[0][3]) < 5]
        return self.cluster_lines_to_strings(horizontal)

    def enhance_contrast(self, image: np.ndarray) -> np.ndarray:
        """Enhance handwritten characters."""
        # CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        return clahe.apply(image)

    def binarize(self, image: np.ndarray) -> np.ndarray:
        """Adaptive thresholding for varied lighting."""
        return cv2.adaptiveThreshold(
            image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
```

### Step 3.2: Custom Tesseract Configuration

**Optimize for tab notation:**

```python
# ocr_tabber/core/ocr_engine.py

import pytesseract
from PIL import Image

class TabOCREngine:
    """OCR engine optimized for guitar tablature."""

    # Characters that appear in guitar tabs
    TAB_WHITELIST = "0123456789ABCDEFGabcdefghprsxX-/\\|~()^"

    def __init__(self, tessdata_path: str = None):
        self.config = self._build_config()
        if tessdata_path:
            pytesseract.pytesseract.tesseract_cmd = tessdata_path

    def _build_config(self) -> str:
        """Build Tesseract configuration string."""
        return (
            f'--psm 6 '  # Assume uniform block of text
            f'-c tessedit_char_whitelist={self.TAB_WHITELIST} '
            f'-c preserve_interword_spaces=1 '
            f'--oem 3'  # Use LSTM + legacy engine
        )

    def recognize(self, image: Image.Image) -> str:
        """Perform OCR on preprocessed tab image."""
        return pytesseract.image_to_string(image, config=self.config)

    def recognize_with_boxes(self, image: Image.Image) -> list:
        """Get character positions for overlay display."""
        data = pytesseract.image_to_data(
            image, config=self.config, output_type=pytesseract.Output.DICT
        )
        return self._parse_box_data(data)
```

### Step 3.3: Training Custom Model (Advanced)

For significantly better handwritten recognition:

```bash
# Steps to train custom Tesseract model:
# 1. Collect 500+ handwritten tab images
# 2. Create ground truth transcriptions
# 3. Use tesseract training tools

# Generate training data
tesseract handwritten_tab_001.png handwritten_tab_001 --psm 6 lstm.train

# Fine-tune existing model
lstmtraining \
  --model_output ./output/handwritten_tabs \
  --continue_from eng.lstm \
  --traineddata eng.traineddata \
  --train_listfile training_files.txt \
  --max_iterations 10000
```

---

## Phase 4: Tab Parsing & Chord Recognition

### Step 4.1: Modernized Tab Parser

```python
# ocr_tabber/core/tab_parser.py

from dataclasses import dataclass
from typing import List, Optional
import re

@dataclass
class Note:
    string: int      # 1-6 (high E to low E)
    fret: int        # 0-24
    position: int    # Horizontal position in tab
    technique: Optional[str] = None  # h, p, /, \, ~, etc.

@dataclass
class Chord:
    notes: List[Note]
    position: int
    name: Optional[str] = None

@dataclass
class TabMeasure:
    chords: List[Chord]
    notes: List[Note]

class TabParser:
    """Parse OCR'd ASCII tab into structured data."""

    STANDARD_TUNING = ['e', 'B', 'G', 'D', 'A', 'E']  # High to low

    def parse(self, raw_text: str) -> List[TabMeasure]:
        """Parse raw OCR text into structured tab data."""
        lines = self._extract_tab_lines(raw_text)
        if len(lines) != 6:
            raise ValueError(f"Expected 6 tab lines, got {len(lines)}")

        measures = self._split_into_measures(lines)
        return [self._parse_measure(m) for m in measures]

    def _extract_tab_lines(self, text: str) -> List[str]:
        """Extract the 6 string lines from raw text."""
        lines = text.strip().split('\n')
        tab_lines = []

        for line in lines:
            # Match lines that look like: "e|---0---2---|"
            if re.match(r'^[eEBGDA]\|.*\|?$', line.strip()):
                tab_lines.append(line)

        return tab_lines

    def _parse_measure(self, lines: List[str]) -> TabMeasure:
        """Parse a single measure into notes and chords."""
        notes = []

        for string_num, line in enumerate(lines, 1):
            # Extract fret numbers and positions
            for match in re.finditer(r'(\d{1,2}|[hpbs/\\~x])', line):
                value = match.group(1)
                position = match.start()

                if value.isdigit():
                    notes.append(Note(
                        string=string_num,
                        fret=int(value),
                        position=position
                    ))
                else:
                    # Technique marker
                    notes.append(Note(
                        string=string_num,
                        fret=-1,
                        position=position,
                        technique=value
                    ))

        # Group simultaneous notes into chords
        chords = self._group_into_chords(notes)

        return TabMeasure(chords=chords, notes=notes)

    def _group_into_chords(self, notes: List[Note]) -> List[Chord]:
        """Group notes at same position into chords."""
        from itertools import groupby

        sorted_notes = sorted(notes, key=lambda n: n.position)
        chords = []

        for pos, group in groupby(sorted_notes, key=lambda n: n.position):
            chord_notes = list(group)
            if len(chord_notes) >= 2:  # At least 2 notes = chord
                chords.append(Chord(notes=chord_notes, position=pos))

        return chords
```

### Step 4.2: Modernized Chord Database

**Convert XML to JSON for better performance:**

```python
# ocr_tabber/database/chord_db.py

import json
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class ChordVoicing:
    frets: List[Optional[int]]  # [None, 0, 2, 2, 2, 0] for A major
    fingers: List[int]
    barre: Optional[int] = None

@dataclass
class ChordDefinition:
    name: str
    root: str
    chord_type: str  # major, minor, 7, etc.
    voicings: List[ChordVoicing]

class ChordDatabase:
    """Fast chord lookup database."""

    def __init__(self, db_path: Path):
        self._db: Dict[str, ChordDefinition] = {}
        self._signature_index: Dict[str, List[str]] = {}
        self._load_database(db_path)

    def _load_database(self, path: Path):
        """Load JSON chord database."""
        with open(path) as f:
            data = json.load(f)

        for chord_data in data['chords']:
            chord = ChordDefinition(**chord_data)
            self._db[chord.name] = chord

            # Build signature index for fast lookup
            for voicing in chord.voicings:
                sig = self._compute_signature(voicing.frets)
                if sig not in self._signature_index:
                    self._signature_index[sig] = []
                self._signature_index[sig].append(chord.name)

    def identify_chord(self, frets: List[Optional[int]]) -> List[str]:
        """Identify chord name from fret positions."""
        sig = self._compute_signature(frets)
        return self._signature_index.get(sig, [])

    def _compute_signature(self, frets: List[Optional[int]]) -> str:
        """Create hashable signature from fret positions."""
        return ','.join(str(f) if f is not None else 'x' for f in frets)

    def get_chord(self, name: str) -> Optional[ChordDefinition]:
        """Get chord definition by name."""
        return self._db.get(name)

    def search(self, query: str) -> List[ChordDefinition]:
        """Search chords by partial name."""
        query = query.lower()
        return [c for n, c in self._db.items() if query in n.lower()]
```

---

## Phase 5: Export Functionality

### Step 5.1: ASCII Tab Export

```python
# ocr_tabber/export/ascii_export.py

class ASCIITabExporter:
    """Export to clean ASCII tab format."""

    def export(self, measures: List[TabMeasure],
               line_width: int = 80) -> str:
        """Export parsed tab to ASCII format."""
        output_lines = [[] for _ in range(6)]  # 6 strings

        for measure in measures:
            measure_width = self._calculate_measure_width(measure)

            for string in range(6):
                line = self._render_string(measure, string, measure_width)
                output_lines[string].append(line)

        # Join measures with bar lines
        return self._format_output(output_lines, line_width)
```

### Step 5.2: MusicXML Export

```python
# ocr_tabber/export/musicxml_export.py

from music21 import stream, note, chord, tablature

class MusicXMLExporter:
    """Export to MusicXML for Guitar Pro, MuseScore, etc."""

    TUNING = [64, 59, 55, 50, 45, 40]  # MIDI notes for standard tuning

    def export(self, measures: List[TabMeasure]) -> str:
        """Export to MusicXML string."""
        score = stream.Score()
        part = stream.Part()
        part.insert(0, tablature.FretBoard())

        for measure_data in measures:
            measure = stream.Measure()

            for chord_data in measure_data.chords:
                if len(chord_data.notes) == 1:
                    n = self._create_note(chord_data.notes[0])
                    measure.append(n)
                else:
                    c = self._create_chord(chord_data.notes)
                    measure.append(c)

            part.append(measure)

        score.append(part)
        return score.write('musicxml')

    def _create_note(self, tab_note: Note) -> note.Note:
        """Convert tab note to music21 note."""
        midi_pitch = self.TUNING[tab_note.string - 1] + tab_note.fret
        n = note.Note(midi_pitch)
        n.articulations.append(
            tablature.FretIndication(tab_note.fret)
        )
        return n
```

### Step 5.3: MIDI Export

```python
# ocr_tabber/export/midi_export.py

from mido import MidiFile, MidiTrack, Message

class MIDIExporter:
    """Export tabs to MIDI for playback."""

    TUNING = [64, 59, 55, 50, 45, 40]  # Standard tuning MIDI notes

    def export(self, measures: List[TabMeasure],
               tempo: int = 120,
               output_path: str = None) -> MidiFile:
        """Export to MIDI file."""
        mid = MidiFile()
        track = MidiTrack()
        mid.tracks.append(track)

        # Set tempo
        track.append(Message('program_change', program=25))  # Steel guitar

        ticks_per_beat = mid.ticks_per_beat

        for measure in measures:
            for chord_data in measure.chords:
                for note in chord_data.notes:
                    if note.fret >= 0:
                        pitch = self.TUNING[note.string - 1] + note.fret
                        track.append(Message('note_on', note=pitch,
                                           velocity=64, time=0))

                # Note duration
                track.append(Message('note_off', time=ticks_per_beat // 2))

        if output_path:
            mid.save(output_path)

        return mid
```

---

## Phase 6: Cross-Platform Packaging

### Step 6.1: PyInstaller Configuration

**Create `build.spec`:**

```python
# build.spec - PyInstaller specification

block_cipher = None

a = Analysis(
    ['ocr_tabber/__main__.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('data/chords/*.json', 'data/chords'),
        ('data/tessdata/*', 'data/tessdata'),
        ('resources/icons/*', 'resources/icons'),
        ('resources/themes/*', 'resources/themes'),
    ],
    hiddenimports=[
        'PySide6.QtSvg',
        'PySide6.QtPrintSupport',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='OCR-Tabber',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/icons/app_icon.ico',  # Windows
)

# macOS app bundle
app = BUNDLE(
    exe,
    name='OCR-Tabber.app',
    icon='resources/icons/app_icon.icns',
    bundle_identifier='com.ocrtabber.app',
    info_plist={
        'NSHighResolutionCapable': True,
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleDocumentTypes': [
            {
                'CFBundleTypeName': 'Image Files',
                'CFBundleTypeExtensions': ['png', 'jpg', 'jpeg', 'bmp'],
                'CFBundleTypeRole': 'Editor',
            }
        ],
    },
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='OCR-Tabber',
)
```

### Step 6.2: Platform-Specific Build Scripts

**Create `scripts/build.py`:**

```python
#!/usr/bin/env python3
"""Build script for all platforms."""

import subprocess
import platform
import shutil
from pathlib import Path

def build_windows():
    """Build Windows executable."""
    subprocess.run([
        'pyinstaller',
        '--clean',
        '--noconfirm',
        'build.spec'
    ])

    # Create installer with NSIS or Inno Setup
    subprocess.run([
        'iscc', 'installer/windows_installer.iss'
    ])

def build_macos():
    """Build macOS app bundle."""
    subprocess.run([
        'pyinstaller',
        '--clean',
        '--noconfirm',
        'build.spec'
    ])

    # Create DMG
    subprocess.run([
        'create-dmg',
        '--volname', 'OCR-Tabber',
        '--window-size', '600', '400',
        '--icon', 'OCR-Tabber.app', '150', '150',
        '--app-drop-link', '450', '150',
        'dist/OCR-Tabber.dmg',
        'dist/OCR-Tabber.app'
    ])

    # Code sign (requires Apple Developer account)
    subprocess.run([
        'codesign', '--deep', '--force', '--sign',
        'Developer ID Application: Your Name',
        'dist/OCR-Tabber.app'
    ])

def build_linux():
    """Build Linux packages."""
    subprocess.run([
        'pyinstaller',
        '--clean',
        '--noconfirm',
        'build.spec'
    ])

    # Create AppImage
    subprocess.run([
        'linuxdeploy-x86_64.AppImage',
        '--appdir', 'AppDir',
        '--executable', 'dist/OCR-Tabber/OCR-Tabber',
        '--desktop-file', 'installer/ocr-tabber.desktop',
        '--icon-file', 'resources/icons/app_icon.png',
        '--output', 'appimage'
    ])

    # Create .deb package
    subprocess.run(['dpkg-deb', '--build', 'debian_package'])

if __name__ == '__main__':
    system = platform.system()
    if system == 'Windows':
        build_windows()
    elif system == 'Darwin':
        build_macos()
    elif system == 'Linux':
        build_linux()
```

### Step 6.3: CI/CD Pipeline

**Create `.github/workflows/build.yml`:**

```yaml
name: Build Desktop Apps

on:
  push:
    tags:
      - 'v*'
  workflow_dispatch:

jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pyinstaller

      - name: Install Tesseract
        run: choco install tesseract

      - name: Build executable
        run: pyinstaller --clean --noconfirm build.spec

      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: OCR-Tabber-Windows
          path: dist/OCR-Tabber/

  build-macos:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pyinstaller
          brew install tesseract create-dmg

      - name: Build app bundle
        run: pyinstaller --clean --noconfirm build.spec

      - name: Create DMG
        run: |
          create-dmg \
            --volname "OCR-Tabber" \
            --window-size 600 400 \
            "dist/OCR-Tabber.dmg" \
            "dist/OCR-Tabber.app"

      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: OCR-Tabber-macOS
          path: dist/OCR-Tabber.dmg

  build-linux:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y tesseract-ocr libxcb-cursor0
          pip install -r requirements.txt
          pip install pyinstaller

      - name: Build executable
        run: pyinstaller --clean --noconfirm build.spec

      - name: Create AppImage
        run: |
          wget -q https://github.com/linuxdeploy/linuxdeploy/releases/download/continuous/linuxdeploy-x86_64.AppImage
          chmod +x linuxdeploy-x86_64.AppImage
          ./linuxdeploy-x86_64.AppImage --appdir AppDir --output appimage

      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: OCR-Tabber-Linux
          path: "*.AppImage"

  release:
    needs: [build-windows, build-macos, build-linux]
    runs-on: ubuntu-latest
    if: startsWith(github.ref, 'refs/tags/')
    steps:
      - name: Download all artifacts
        uses: actions/download-artifact@v4

      - name: Create Release
        uses: softprops/action-gh-release@v1
        with:
          files: |
            OCR-Tabber-Windows/*
            OCR-Tabber-macOS/*
            OCR-Tabber-Linux/*
```

---

## Phase 7: Testing Strategy

### Step 7.1: Unit Tests

```python
# tests/test_tab_parser.py

import pytest
from ocr_tabber.core.tab_parser import TabParser, Note, Chord

class TestTabParser:
    @pytest.fixture
    def parser(self):
        return TabParser()

    def test_parse_simple_tab(self, parser):
        raw_tab = """
e|---0---2---3---|
B|---0---3---3---|
G|---1---2---0---|
D|---2---0---0---|
A|---2---0---2---|
E|---0---x---3---|
"""
        measures = parser.parse(raw_tab)

        assert len(measures) == 1
        assert len(measures[0].chords) == 3  # 3 chords

    def test_detect_hammer_on(self, parser):
        raw_tab = """
e|---0h2---------|
B|---------------|
G|---------------|
D|---------------|
A|---------------|
E|---------------|
"""
        measures = parser.parse(raw_tab)
        notes = [n for n in measures[0].notes if n.technique == 'h']

        assert len(notes) == 1

    def test_invalid_tab_raises_error(self, parser):
        with pytest.raises(ValueError):
            parser.parse("not a tab")
```

### Step 7.2: Integration Tests

```python
# tests/test_ocr_integration.py

import pytest
from pathlib import Path
from PIL import Image
from ocr_tabber.core.ocr_engine import TabOCREngine
from ocr_tabber.core.image_processor import TabImageProcessor
from ocr_tabber.core.tab_parser import TabParser

class TestOCRIntegration:
    @pytest.fixture
    def sample_images(self):
        return list(Path('tests/fixtures/tab_images').glob('*.png'))

    @pytest.fixture
    def ground_truth(self):
        truths = {}
        for txt in Path('tests/fixtures/ground_truth').glob('*.txt'):
            truths[txt.stem] = txt.read_text()
        return truths

    def test_ocr_accuracy(self, sample_images, ground_truth):
        processor = TabImageProcessor()
        ocr = TabOCREngine()
        parser = TabParser()

        accuracies = []

        for img_path in sample_images:
            image = Image.open(img_path)
            processed = processor.process(image)
            raw_text = ocr.recognize(processed)

            expected = ground_truth.get(img_path.stem)
            if expected:
                accuracy = self._calculate_accuracy(raw_text, expected)
                accuracies.append(accuracy)

        avg_accuracy = sum(accuracies) / len(accuracies)
        assert avg_accuracy > 0.85  # 85% minimum accuracy
```

---

## Phase 8: UI/UX Design

### Step 8.1: Main Window Layout

```
┌─────────────────────────────────────────────────────────────────────────┐
│  File  Edit  View  Tools  Help                              [─] [□] [×] │
├─────────────────────────────────────────────────────────────────────────┤
│  [📂 Open] [📷 Capture] [🔄 Convert] [💾 Save] [📤 Export]              │
├────────────────────────────────┬────────────────────────────────────────┤
│                                │                                        │
│    ┌──────────────────────┐    │   ┌──────────────────────────────┐    │
│    │                      │    │   │ e|---0---2---3---0---2---3---|    │
│    │   [Drag & Drop       │    │   │ B|---0---3---3---0---3---3---|    │
│    │    Image Here]       │    │   │ G|---1---2---0---1---2---0---|    │
│    │                      │    │   │ D|---2---0---0---2---0---0---|    │
│    │   or click to browse │    │   │ A|---2---0---2---2---0---2---|    │
│    │                      │    │   │ E|---0---x---3---0---x---3---|    │
│    └──────────────────────┘    │   └──────────────────────────────┘    │
│                                │                                        │
│    [🔍 Zoom: 100%] [⟲ Rotate]  │   Detected Chords:                     │
│                                │   [Am] [G] [C] [Am] [G] [C]            │
│    Processing Options:         │                                        │
│    ☑ Auto-deskew              │   ┌─────┬─────┬─────┐                  │
│    ☑ Enhance contrast         │   │ Am  │  G  │  C  │                  │
│    ☐ Manual regions           │   │x0221│32003│x3201│                  │
│                                │   └─────┴─────┴─────┘                  │
│                                │                                        │
├────────────────────────────────┴────────────────────────────────────────┤
│  Ready                                              [▓▓▓▓▓▓▓▓▓▓] 100%   │
└─────────────────────────────────────────────────────────────────────────┘
```

### Step 8.2: Key User Flows

**Flow 1: Quick Convert**
1. User drags image onto window
2. App automatically processes image
3. Shows detected tab in editor
4. User clicks Export → chooses format
5. Done!

**Flow 2: Manual Correction**
1. User opens image
2. Clicks "Convert"
3. Reviews detected tab
4. Edits any OCR errors directly
5. Clicks detected chord to see alternatives
6. Exports corrected tab

**Flow 3: Batch Processing**
1. User selects multiple images
2. App queues processing
3. Progress shown for each
4. Results saved to output folder

---

## Phase 9: Implementation Timeline

### Milestone 1: Foundation (Weeks 1-2)
- [ ] Python 3 migration complete
- [ ] New project structure in place
- [ ] Dependencies installed and working
- [ ] Basic test suite running

### Milestone 2: Core Engine (Weeks 3-4)
- [ ] Image preprocessing pipeline
- [ ] Modernized OCR engine with pytesseract
- [ ] Tab parser with chord detection
- [ ] JSON chord database

### Milestone 3: Basic UI (Weeks 5-6)
- [ ] PySide6 main window shell
- [ ] Image input panel with drag-drop
- [ ] Tab output display
- [ ] Basic convert functionality end-to-end

### Milestone 4: Full Features (Weeks 7-8)
- [ ] Export to ASCII, MusicXML, MIDI
- [ ] Chord diagrams display
- [ ] Tab editor with syntax highlighting
- [ ] Settings/preferences dialog

### Milestone 5: Polish & Package (Weeks 9-10)
- [ ] Cross-platform testing
- [ ] PyInstaller builds working
- [ ] Installers for each platform
- [ ] CI/CD pipeline complete

### Milestone 6: Release (Week 11+)
- [ ] Beta testing
- [ ] Documentation
- [ ] v1.0 release

---

## Technical Requirements Summary

### Dependencies
| Package | Version | Purpose |
|---------|---------|---------|
| Python | 3.11+ | Runtime |
| PySide6 | 6.6+ | Desktop UI |
| pytesseract | 0.3.10+ | OCR engine |
| Pillow | 10.0+ | Image handling |
| OpenCV | 4.8+ | Image preprocessing |
| music21 | 9.0+ | MusicXML export |
| mido | 1.3+ | MIDI export |
| PyInstaller | 6.0+ | App bundling |

### External Dependencies
- **Tesseract OCR 5.x** - Must be installed on system
- System fonts for tab display

### Supported Platforms
- **Windows**: 10, 11 (x64)
- **macOS**: 11+ (Intel & Apple Silicon)
- **Linux**: Ubuntu 20.04+, Fedora 35+, Debian 11+ (x64)

### Estimated Bundle Sizes
- Windows: ~150-200 MB (includes Tesseract)
- macOS: ~180-220 MB (.app bundle)
- Linux: ~140-180 MB (AppImage)

---

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Poor handwritten OCR accuracy | High | Custom Tesseract training, manual correction UI |
| Cross-platform UI inconsistencies | Medium | Extensive testing, Qt's native rendering |
| Tesseract installation complexity | Medium | Bundle Tesseract with app |
| Large bundle size | Low | UPX compression, selective packaging |
| macOS code signing cost | Low | Use ad-hoc signing for beta, get cert for release |

---

## Next Steps

1. **Immediate**: Begin Python 3 migration
2. **This week**: Set up new project structure
3. **Next week**: Implement basic PySide6 window
4. **Ongoing**: Build test suite alongside features

---

*Plan created: 2026-01-17*
*Target completion: ~10-12 weeks*
