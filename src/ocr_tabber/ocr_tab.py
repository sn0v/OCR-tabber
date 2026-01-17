#!/usr/bin/env python3
# Copyright 2014 Utkarsh Jaiswal
# Updated 2026 - Modernized for Python 3

"""
Scans an input image containing a guitar tab and converts it into ASCII.
Uses pytesseract (modern Python wrapper for Tesseract OCR).
"""

import sys
from pathlib import Path
from typing import Optional

try:
    import pytesseract
    from PIL import Image
except ImportError as e:
    print(f"Error: Required dependencies not installed: {e}", file=sys.stderr)
    print("Install with: pip install -e .[dev]", file=sys.stderr)
    sys.exit(1)


def process_tab_image(image_path: Path, tessdata_dir: Optional[Path] = None) -> str:
    """
    Process a guitar tab image and extract ASCII text using OCR.

    Args:
        image_path: Path to the image file containing guitar tablature
        tessdata_dir: Optional path to tessdata directory (for custom trained data)

    Returns:
        The extracted text from the image

    Raises:
        FileNotFoundError: If the image file doesn't exist
        pytesseract.TesseractError: If OCR processing fails
    """
    if not image_path.exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")

    # Open image using Pillow
    image = Image.open(image_path)

    # Configure Tesseract options
    # Character whitelist restricts to characters found in guitar tabs
    custom_config = r'--psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGabcdefghp-/|'

    # Set tessdata directory if provided
    if tessdata_dir:
        pytesseract.pytesseract.tesseract_cmd = str(tessdata_dir / "tesseract")

    # Perform OCR
    result = pytesseract.image_to_string(image, lang="eng", config=custom_config)

    return result.strip()


def main() -> int:
    """
    Main entry point for the ocr-tab command-line tool.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    if len(sys.argv) < 2:
        print("Usage: ocr-tab <image_path>", file=sys.stderr)
        print("Example: ocr-tab tab_image.png", file=sys.stderr)
        return 1

    image_path = Path(sys.argv[1])

    try:
        result = process_tab_image(image_path)
        print("OCRed tab:")
        print(result)
        return 0
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except pytesseract.TesseractError as e:
        print(f"Tesseract OCR Error: {e}", file=sys.stderr)
        print(
            "Make sure Tesseract is installed on your system:", file=sys.stderr
        )
        print("  Ubuntu/Debian: sudo apt-get install tesseract-ocr", file=sys.stderr)
        print("  macOS: brew install tesseract", file=sys.stderr)
        print("  Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
