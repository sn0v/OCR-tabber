"""Image preprocessing pipeline to improve OCR quality for guitar tabs."""

from PIL import Image, ImageFilter, ImageOps

# Default preprocessing steps applied in order
DEFAULT_STEPS = ["grayscale", "threshold", "resize"]


def grayscale(image: Image.Image) -> Image.Image:
    """
    Convert an image to grayscale.

    Args:
        image: A PIL Image object.

    Returns:
        A new grayscale PIL Image.
    """
    return ImageOps.grayscale(image)


def threshold(image: Image.Image, threshold: int = 128) -> Image.Image:
    """
    Apply binary thresholding for cleaner text.

    Pixels above the threshold become white (255), pixels at or below
    become black (0). If the image is not already grayscale, it is
    converted first.

    Args:
        image: A PIL Image object.
        threshold: Pixel intensity cutoff (0-255). Default is 128.

    Returns:
        A new binary (black and white) PIL Image.
    """
    if image.mode != "L":
        image = ImageOps.grayscale(image)
    return image.point(lambda px: 255 if px > threshold else 0, mode="L")


def resize(image: Image.Image, scale_factor: float = 2.0) -> Image.Image:
    """
    Upscale an image for better OCR on small images.

    Args:
        image: A PIL Image object.
        scale_factor: Multiplier for width and height. Default is 2.0.

    Returns:
        A new resized PIL Image.

    Raises:
        ValueError: If scale_factor is not positive.
    """
    if scale_factor <= 0:
        raise ValueError(f"scale_factor must be positive, got {scale_factor}")
    new_width = int(image.width * scale_factor)
    new_height = int(image.height * scale_factor)
    return image.resize((new_width, new_height), Image.Resampling.LANCZOS)


def deskew(image: Image.Image) -> Image.Image:
    """
    Basic rotation correction for slightly tilted images.

    Uses a simple heuristic: converts to grayscale, applies edge detection,
    then tests small rotation angles to find the one that maximises the
    variance of row-wise pixel sums (indicating horizontal alignment of
    text lines).

    The search range is -5 to +5 degrees in 0.5-degree steps, which covers
    the typical range of scanner or camera tilt.

    Args:
        image: A PIL Image object.

    Returns:
        A new deskewed PIL Image (same mode as input).
    """
    # Work on a grayscale copy for analysis
    if image.mode != "L":
        gray = ImageOps.grayscale(image)
    else:
        gray = image.copy()

    # Edge detection to highlight text lines
    edges = gray.filter(ImageFilter.FIND_EDGES)

    best_angle = 0.0
    best_variance = -1.0

    # Test small rotation angles
    for tenth in range(-50, 51, 5):  # -5.0 to +5.0 in 0.5 steps
        angle = tenth / 10.0
        rotated = edges.rotate(angle, resample=Image.Resampling.BICUBIC, fillcolor=0)
        # Compute row-wise sums
        pixels = list(rotated.getdata())
        width = rotated.width
        height = rotated.height
        row_sums = []
        for row_idx in range(height):
            row_start = row_idx * width
            row_sums.append(sum(pixels[row_start : row_start + width]))
        if not row_sums:
            continue
        mean = sum(row_sums) / len(row_sums)
        variance = sum((s - mean) ** 2 for s in row_sums) / len(row_sums)
        if variance > best_variance:
            best_variance = variance
            best_angle = angle

    if best_angle == 0.0:
        return image

    return image.rotate(best_angle, resample=Image.Resampling.BICUBIC, expand=True, fillcolor=255)


# Registry mapping step names to functions
STEP_REGISTRY: dict[str, callable] = {
    "grayscale": grayscale,
    "threshold": threshold,
    "resize": resize,
    "deskew": deskew,
}


def preprocess(image: Image.Image, steps: list[str] | None = None) -> Image.Image:
    """
    Main preprocessing pipeline that chains selected steps together.

    Default steps: grayscale -> threshold -> resize.

    Args:
        image: A PIL Image object to preprocess.
        steps: List of step names to apply in order. If None, uses
               DEFAULT_STEPS (grayscale, threshold, resize).

    Returns:
        A new preprocessed PIL Image.

    Raises:
        ValueError: If an unknown step name is provided.
    """
    if steps is None:
        steps = DEFAULT_STEPS

    result = image.copy()
    for step_name in steps:
        func = STEP_REGISTRY.get(step_name)
        if func is None:
            raise ValueError(
                f"Unknown preprocessing step: '{step_name}'. "
                f"Available steps: {', '.join(sorted(STEP_REGISTRY.keys()))}"
            )
        result = func(result)

    return result
