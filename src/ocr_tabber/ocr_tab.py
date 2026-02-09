# Scans an input image containing a guitar tab and converts it into ASCII
# Uses pytesseract for OCR

import sys
from pathlib import Path

import pytesseract
from PIL import Image

from ocr_tabber.preprocessing import preprocess as preprocess_image

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


def ocr_tab_image(image_path: str, preprocess: bool = True) -> str:
    """
    Perform OCR on a guitar tab image and return the recognized text.

    Args:
        image_path: Path to the image file containing guitar tablature.
        preprocess: Whether to run the image through the preprocessing
                    pipeline before OCR. Defaults to True.

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

    if preprocess:
        image = preprocess_image(image)

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


def collect_image_paths(source: str) -> list[Path]:
    """
    Collect image file paths from a directory, glob pattern, or single file path.

    Args:
        source: A directory path, glob pattern, or single image file path.

    Returns:
        List of Path objects for valid image files found.

    Raises:
        FileNotFoundError: If the source path doesn't exist (for non-glob inputs).
        ValueError: If no valid image files are found.
    """
    source_path = Path(source)

    # Check if the source is a glob pattern (contains * or ?)
    if '*' in source or '?' in source:
        # Use the parent directory for globbing
        # If the pattern is relative, resolve from cwd
        if source_path.is_absolute():
            base_dir = Path(source_path.anchor)
            pattern = str(source_path.relative_to(base_dir))
        else:
            base_dir = Path.cwd()
            pattern = source

        paths = sorted(base_dir.glob(pattern))
        image_paths = [
            p for p in paths
            if p.is_file() and p.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS
        ]
    elif source_path.is_dir():
        # Collect all supported image files from the directory
        image_paths = sorted(
            p for p in source_path.iterdir()
            if p.is_file() and p.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS
        )
    elif source_path.is_file():
        # Single file
        if source_path.suffix.lower() not in SUPPORTED_IMAGE_EXTENSIONS:
            raise ValueError(
                f"Unsupported image format: {source_path.suffix}. "
                f"Supported formats: {', '.join(sorted(SUPPORTED_IMAGE_EXTENSIONS))}"
            )
        image_paths = [source_path]
    else:
        raise FileNotFoundError(f"Path not found: {source}")

    if not image_paths:
        raise ValueError(f"No valid image files found in: {source}")

    return image_paths


def batch_ocr_images(sources: list[str]) -> list[dict[str, str | None]]:
    """
    Process multiple images through OCR and return results for each.

    Each image is processed independently; errors in one image do not
    prevent processing of others.

    Args:
        sources: List of source paths (directories, glob patterns, or file paths).

    Returns:
        List of result dicts with keys:
            - 'file': The image file path as a string
            - 'result': The OCR text result, or None if processing failed
            - 'error': Error message string, or None if processing succeeded
    """
    # Collect all image paths from all sources
    all_image_paths: list[Path] = []
    results: list[dict[str, str | None]] = []

    for source in sources:
        try:
            paths = collect_image_paths(source)
            all_image_paths.extend(paths)
        except (FileNotFoundError, ValueError) as e:
            results.append({
                'file': source,
                'result': None,
                'error': str(e),
            })

    # Process each image
    for image_path in all_image_paths:
        try:
            text = ocr_tab_image(str(image_path))
            results.append({
                'file': str(image_path),
                'result': text,
                'error': None,
            })
        except (FileNotFoundError, ValueError, OSError, RuntimeError) as e:
            results.append({
                'file': str(image_path),
                'result': None,
                'error': str(e),
            })

    return results


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
