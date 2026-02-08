# OCR-tabber Feature Plan

This document outlines planned features for OCR-tabber, prioritized by value and implementation order.

---

## Current State (as of February 2026)

The following core capabilities are implemented and working:

- [x] **CLI with argparse** -- 3 subcommands (`ocr`, `recognize`, `build-db`) with flags (`-o`, `-t`, `--version`), proper exit codes
- [x] **OCR via pytesseract** -- `ocr_tab.py` accepts an image, configures Tesseract with `--psm 6` (single block mode) and a character whitelist for tab characters (`0-9`, `A-G`, `a-g`, `h`, `p`, `-/|`)
- [x] **Chord recognition** -- `chord_recognizer.py` parses ASCII tab files, identifies simultaneous notes (same horizontal position), and matches against a 512-chord pickle database
- [x] **Database builder** -- `tab_db_extractor.py` parses Gnome Guitar XML format and outputs `mainDB.pkl`
- [x] **Input validation** -- Image extension checking (`SUPPORTED_IMAGE_EXTENSIONS`), tab file content validation (key count, note format)
- [x] **Error handling** -- All file I/O wrapped in try/except with descriptive error messages
- [x] **Test suite** -- 29 tests across 3 modules with shared fixtures in `conftest.py`

---

## MVP+ (Build First)

These features form the core product that's actually useful end-to-end.

1. **Validate OCR accuracy** -- Test current Tesseract approach with real tab images (not yet validated with real-world images; current test data is `ASCIItab.txt` only)
2. **Image preprocessing pipeline** -- Deskew, contrast adjustment, noise removal (not started; `ocr_tab.py` passes raw image directly to Tesseract)
3. **Confidence scoring** -- Return confidence levels for recognition results (not started; uses `image_to_string()` which returns plain text without confidence data)
4. **Simple correction UI** -- Let users fix OCR errors quickly (not started; no GUI exists)
5. **Chord diagram generation** -- Visual fingering charts alongside text output (not started; output is text-only)

---

## High Priority (Core Value)

| Feature | Description | Status | Notes |
|---------|-------------|--------|-------|
| Image preprocessing | Deskew, contrast, denoise before OCR | Not started | Pillow is already a dependency and could be used for basic preprocessing |
| Confidence scoring | Return confidence % for each recognized element | Not started | Would require switching from `image_to_string()` to `image_to_data()` in pytesseract |
| Manual correction UI | Edit/fix OCR mistakes in the GUI | Not started | Blocked by GUI toolkit decision |
| Multiple output formats | Plain text, JSON, MusicXML export | Not started | CLI currently only outputs plain text (stdout or `-o` file) |
| Chord diagram generation | Visual fingering charts (SVG/PNG) | Not started | No image generation dependencies present |
| Batch processing | Process a folder of images at once | Not started | `cmd_ocr()` accepts a single `args.image` path only |

---

## Medium Priority (Expand Use Cases)

| Feature | Description | Status | Notes |
|---------|-------------|--------|-------|
| PDF/multi-page support | Parse entire songbook PDFs | Not started | `validate_image_path()` explicitly rejects `.pdf` extension |
| Bass tab support | Handle 4-string bass tablature | Not started | `parse_tab_file()` raises `ValueError` if string count exceeds 6; hardcoded 6-string assumption |
| Alternative tunings | Drop D, Open G, DADGAD, etc. | Not started | Key/tuning is read from tab file but chord DB matching assumes standard tuning |
| MIDI export | Convert recognized tabs to MIDI | Not started | No MIDI or audio dependencies |
| Camera capture | Point phone/webcam at tab, scan directly | Not started | No camera/video code |
| Tab library/organizer | Save, tag, search your collection | Not started | No persistence layer beyond file output |
| Audio playback preview | Play back the tab as audio | Not started | No audio dependencies |

---

## Low Priority (Power User / Future)

| Feature | Description | Status |
|---------|-------------|--------|
| Guitar Pro format export | Export to .gp5/.gpx format | Not started |
| Tempo/metronome integration | Set BPM, practice with click track | Not started |
| Loop sections for practice | Repeat specific measures | Not started |
| YouTube video sync | Display tab alongside video playback | Not started |
| Ultimate Guitar integration | Fetch/compare against UG database | Not started |
| Custom ML OCR model | Train model specifically for guitar tabs | Not started |
| Impossible fingering detection | Warn when chord is physically unplayable | Not started |

---

## Technical Decisions

### Language/Framework
- **Current**: Python 3.14.2 + pytesseract + Poetry
- **Considering**: Rust + Tauri, Go + Wails, or Kotlin + Compose Multiplatform
- **Decision**: Validate OCR approach first in Python, then decide on rewrite
- **Status**: Still in Python validation phase. CLI is functional but OCR accuracy has not been systematically tested with real-world tab images.

### OCR Strategy
- **Current**: Tesseract with character whitelist (`0-9 A-G a-g h p - / |`) and PSM 6 (single block)
- **Alternatives to evaluate**:
  - EasyOCR (deep learning based)
  - PaddleOCR (excellent accuracy)
  - Custom CV approach (detect 6 lines, segment columns, template match)
  - Cloud APIs (Google Vision, AWS Textract)
- **Decision**: Test accuracy with real images before committing
- **Status**: No accuracy benchmarks exist yet. The OCR config is set up but needs validation.

### GUI Toolkit
- **Candidates**: Tauri, Wails, Fyne, Compose Multiplatform, Electron
- **Decision**: Depends on language choice above
- **Status**: No GUI work has begun. CLI is the only interface.

### Database Format
- **Current**: Pickle (`mainDB.pkl`) generated from `mainDB.xml`
- **Consideration**: Replace pickle with JSON for security, portability, and human readability
- **Status**: Still using pickle. Listed as a quick win in DEVELOPMENT_PLAN.md.

---

## Success Metrics

- OCR accuracy rate on standard tab images (target: >90%) -- **not yet measured**
- Chord recognition accuracy (target: >95% for chords in database) -- **not yet measured**
- Time to process single image (target: <2 seconds) -- **not yet measured**
- User correction rate (lower is better) -- **not yet measurable** (no correction UI exists)

---

*Created: January 2026*
*Last updated: February 2026 -- verified against actual source code*
