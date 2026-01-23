# OCR-tabber

Scans guitar tab images and converts them to ASCII. Recognizes chords from a 512-chord database.

## Setup

```bash
# Install Tesseract OCR (macOS)
brew install tesseract

# Install Python dependencies
poetry install
```

## Usage

```bash
# OCR a guitar tab image
ocr-tabber ocr tab-image.png
ocr-tabber ocr tab-image.png -o output.txt

# Recognize chords from ASCII tab
ocr-tabber recognize
ocr-tabber recognize -t my-tab.txt

# Rebuild chord database
ocr-tabber build-db
```

## License

Apache 2.0 - see [LICENSE.md](LICENSE.md)

Chord database from [Gnome Guitar](http://gnome-chord.sourceforge.net/) (GPL 2.0).
