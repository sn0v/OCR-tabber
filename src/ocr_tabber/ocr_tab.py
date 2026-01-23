# Scans an input image containing a guitar tab and converts it into ASCII
# Uses pytesseract for OCR

import sys
from pathlib import Path

import pytesseract
from PIL import Image

# Get the data directory path relative to this module
DATA_DIR = Path(__file__).parent.parent.parent / "data"
TESSDATA_DIR = DATA_DIR / "tessdata"

# Supported image file extensions
SUPPORTED_IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.tif', '.webp'}


def validate_image_path(image_path: str) -> Path:
    """
    Validate that the image path exists and has a supported extension.

    Args:
        image_path: Path to the image file.

    Returns:
        Path object for the validated image path.

    Raises:
        FileNotFoundError: If the image file doesn't exist.
        ValueError: If the file extension is not supported.
    """
    img_path = Path(image_path)

    if not img_path.exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")

    if img_path.suffix.lower() not in SUPPORTED_IMAGE_EXTENSIONS:
        raise ValueError(
            f"Unsupported image format: {img_path.suffix}. "
            f"Supported formats: {', '.join(sorted(SUPPORTED_IMAGE_EXTENSIONS))}"
        )

    return img_path


def ocr_tab_image(image_path: str) -> str:
    """
    Perform OCR on a guitar tab image and return the recognized text.

    Args:
        image_path: Path to the image file containing guitar tablature.

    Returns:
        The OCR result as a string.

    Raises:
        FileNotFoundError: If the image file doesn't exist.
        ValueError: If the file extension is not supported.
        IOError: If the image cannot be read.
    """
    img_path = validate_image_path(image_path)

    try:
        image = Image.open(img_path)
    except Exception as e:
        raise OSError(f"Failed to open image file: {image_path}") from e

    # Configure tesseract for guitar tab recognition
    # Character whitelist restricts characters to ones found in guitar tabs
    custom_config = (
        f"--tessdata-dir {TESSDATA_DIR} "
        "--psm 6 "  # PSM_SINGLE_BLOCK - assume a single uniform block of text
        "-c tessedit_char_whitelist=0123456789ABCDEFGabcdefghp-/|"
    )

    try:
        result = pytesseract.image_to_string(image, lang="eng", config=custom_config)
    except pytesseract.TesseractNotFoundError:
        raise RuntimeError(
            "Tesseract is not installed or not in PATH. "
            "Please install Tesseract OCR: https://github.com/tesseract-ocr/tesseract"
        ) from None
    except Exception as e:
        raise RuntimeError(f"OCR processing failed: {e}") from e

    return result


def main() -> None:
    """Main entry point when running as a script."""
    if len(sys.argv) < 2:
        print("Usage: python ocr_tab.py <image_file>", file=sys.stderr)
        sys.exit(1)

    image_file = sys.argv[1]

    try:
        result = ocr_tab_image(image_file)
        print("OCRed tab -")
        print(result)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except (OSError, RuntimeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
