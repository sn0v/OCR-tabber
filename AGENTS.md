# OCR-tabber Agent Guide

## Project Overview
OCR tool for guitar tablature recognition. Scans images of guitar tabs and converts them to ASCII, then recognizes chords from a database.

## Tech Stack
- **Python 3.14** with Poetry for dependency management
- **pytesseract** for OCR (requires Tesseract installed on system)
- **pytest** for testing

## Project Structure
```
src/ocr_tabber/
├── ocr_tab.py          # OCR processing - converts tab images to text
├── chord_recognizer.py # Identifies chords from ASCII tab notation
├── tab_db_extractor.py # Parses XML chord database to pickle format
└── cli.py              # CLI entry point (stub - not yet implemented)

data/
├── mainDB.xml          # Source chord database (512 chords)
├── mainDB.pkl          # Compiled chord database
├── ASCIItab.txt        # Sample ASCII tab for testing
└── tessdata/           # Tesseract language data
```

## Common Commands
```bash
poetry install              # Install dependencies
poetry run pytest tests/ -v # Run tests
poetry run python -m ocr_tabber.ocr_tab <image>           # OCR an image
poetry run python -m ocr_tabber.chord_recognizer          # Recognize chords
poetry run python -m ocr_tabber.tab_db_extractor          # Rebuild chord DB
```

## Development Notes
- All file paths use `pathlib` relative to module location
- Data files are at project root in `data/` directory
- Input validation exists for image formats and tab file content
- See DEVELOPMENT_PLAN.md for roadmap and technical debt items
