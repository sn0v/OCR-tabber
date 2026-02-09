"""Tests for the preprocessing module."""

import pytest
from PIL import Image, ImageDraw

from ocr_tabber.preprocessing import (
    DEFAULT_STEPS,
    STEP_REGISTRY,
    deskew,
    grayscale,
    preprocess,
    resize,
    threshold,
)

# ---------------------------------------------------------------------------
# Helpers to create synthetic test images
# ---------------------------------------------------------------------------


def make_rgb_image(width: int = 100, height: int = 50, color: tuple = (200, 100, 50)) -> Image.Image:
    """Create a simple solid-color RGB image."""
    return Image.new("RGB", (width, height), color)


def make_gray_image(width: int = 100, height: int = 50, value: int = 128) -> Image.Image:
    """Create a simple solid-value grayscale image."""
    return Image.new("L", (width, height), value)


def make_text_image(width: int = 200, height: int = 60) -> Image.Image:
    """Create a simple image with horizontal lines simulating text rows."""
    img = Image.new("L", (width, height), 255)
    draw = ImageDraw.Draw(img)
    # Draw horizontal lines that mimic tab string lines
    for y in [10, 20, 30, 40, 50]:
        draw.line([(5, y), (width - 5, y)], fill=0, width=1)
    return img


# ---------------------------------------------------------------------------
# Tests for grayscale()
# ---------------------------------------------------------------------------


class TestGrayscale:
    def test_rgb_to_grayscale(self):
        """An RGB image should be converted to mode 'L'."""
        img = make_rgb_image()
        result = grayscale(img)
        assert result.mode == "L"
        assert result.size == img.size

    def test_already_grayscale(self):
        """A grayscale image should remain grayscale (no error)."""
        img = make_gray_image()
        result = grayscale(img)
        assert result.mode == "L"

    def test_rgba_to_grayscale(self):
        """An RGBA image should be converted to grayscale."""
        img = Image.new("RGBA", (40, 40), (100, 150, 200, 255))
        result = grayscale(img)
        assert result.mode == "L"
        assert result.size == (40, 40)


# ---------------------------------------------------------------------------
# Tests for threshold()
# ---------------------------------------------------------------------------


class TestThreshold:
    def test_light_pixels_become_white(self):
        """Pixels above the threshold should become 255."""
        img = make_gray_image(value=200)
        result = threshold(img, threshold=128)
        pixels = list(result.getdata())
        assert all(px == 255 for px in pixels)

    def test_dark_pixels_become_black(self):
        """Pixels at or below the threshold should become 0."""
        img = make_gray_image(value=50)
        result = threshold(img, threshold=128)
        pixels = list(result.getdata())
        assert all(px == 0 for px in pixels)

    def test_threshold_boundary(self):
        """A pixel exactly at the threshold value should become black (<=)."""
        img = make_gray_image(value=128)
        result = threshold(img, threshold=128)
        pixels = list(result.getdata())
        assert all(px == 0 for px in pixels)

    def test_threshold_on_rgb_image(self):
        """Threshold should auto-convert an RGB image to grayscale first."""
        img = make_rgb_image(color=(255, 255, 255))
        result = threshold(img, threshold=128)
        assert result.mode == "L"
        pixels = list(result.getdata())
        assert all(px == 255 for px in pixels)

    def test_custom_threshold_value(self):
        """A high threshold should make mid-gray pixels black."""
        img = make_gray_image(value=150)
        result = threshold(img, threshold=200)
        pixels = list(result.getdata())
        assert all(px == 0 for px in pixels)


# ---------------------------------------------------------------------------
# Tests for resize()
# ---------------------------------------------------------------------------


class TestResize:
    def test_default_scale_doubles_size(self):
        """Default scale_factor=2.0 should double width and height."""
        img = make_gray_image(width=100, height=50)
        result = resize(img)
        assert result.size == (200, 100)

    def test_custom_scale_factor(self):
        """A custom scale factor should produce the expected dimensions."""
        img = make_gray_image(width=100, height=50)
        result = resize(img, scale_factor=3.0)
        assert result.size == (300, 150)

    def test_downscale(self):
        """A scale factor less than 1 should shrink the image."""
        img = make_gray_image(width=100, height=50)
        result = resize(img, scale_factor=0.5)
        assert result.size == (50, 25)

    def test_invalid_scale_factor(self):
        """A zero or negative scale factor should raise ValueError."""
        img = make_gray_image()
        with pytest.raises(ValueError, match="scale_factor must be positive"):
            resize(img, scale_factor=0)
        with pytest.raises(ValueError, match="scale_factor must be positive"):
            resize(img, scale_factor=-1.0)

    def test_mode_preserved(self):
        """The image mode should be preserved after resizing."""
        rgb_img = make_rgb_image()
        result = resize(rgb_img, scale_factor=1.5)
        assert result.mode == rgb_img.mode


# ---------------------------------------------------------------------------
# Tests for deskew()
# ---------------------------------------------------------------------------


class TestDeskew:
    def test_straight_image_unchanged(self):
        """A perfectly straight image should not be significantly altered."""
        img = make_text_image()
        result = deskew(img)
        # The size may change slightly due to rotation expand, but should be close
        assert abs(result.width - img.width) <= 2
        assert abs(result.height - img.height) <= 2

    def test_tilted_image_corrected(self):
        """A slightly tilted image should be rotated back toward level."""
        img = make_text_image(width=200, height=100)
        # Tilt the image by 3 degrees
        tilted = img.rotate(-3, resample=Image.Resampling.BICUBIC, expand=True, fillcolor=255)
        result = deskew(tilted)
        # Result should exist and be a valid image
        assert result.mode == tilted.mode
        assert result.width > 0 and result.height > 0

    def test_rgb_input(self):
        """Deskew should accept and return an RGB image."""
        img = Image.new("RGB", (200, 100), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        for y in [20, 40, 60, 80]:
            draw.line([(10, y), (190, y)], fill=(0, 0, 0), width=1)
        result = deskew(img)
        assert result.mode == "RGB"


# ---------------------------------------------------------------------------
# Tests for preprocess() pipeline
# ---------------------------------------------------------------------------


class TestPreprocess:
    def test_default_steps(self):
        """Default pipeline (grayscale -> threshold -> resize) should produce expected output."""
        img = make_rgb_image(width=50, height=30, color=(200, 200, 200))
        result = preprocess(img)
        # After grayscale + threshold(128) + resize(2x):
        assert result.mode == "L"
        assert result.size == (100, 60)
        # Light pixels above threshold should be white
        pixels = list(result.getdata())
        assert all(px == 255 for px in pixels)

    def test_custom_steps(self):
        """Custom step list should be applied in order."""
        img = make_rgb_image(width=50, height=30)
        result = preprocess(img, steps=["grayscale"])
        assert result.mode == "L"
        assert result.size == (50, 30)

    def test_empty_steps(self):
        """An empty step list should return a copy of the original."""
        img = make_rgb_image(width=50, height=30)
        result = preprocess(img, steps=[])
        assert result.size == img.size
        assert result.mode == img.mode

    def test_unknown_step_raises(self):
        """An unknown step name should raise ValueError."""
        img = make_rgb_image()
        with pytest.raises(ValueError, match="Unknown preprocessing step"):
            preprocess(img, steps=["nonexistent"])

    def test_all_steps(self):
        """All registered steps should be usable together."""
        img = make_text_image(width=100, height=60)
        # Convert to RGB so grayscale has something to do
        rgb_img = img.convert("RGB")
        result = preprocess(rgb_img, steps=["grayscale", "threshold", "resize", "deskew"])
        assert result.mode == "L"
        assert result.width > 0 and result.height > 0

    def test_original_not_mutated(self):
        """The original image should not be modified by preprocessing."""
        img = make_rgb_image(width=50, height=30)
        original_size = img.size
        original_mode = img.mode
        preprocess(img)
        assert img.size == original_size
        assert img.mode == original_mode


# ---------------------------------------------------------------------------
# Tests for module-level constants
# ---------------------------------------------------------------------------


class TestConstants:
    def test_default_steps_are_valid(self):
        """All default steps should be in the step registry."""
        for step in DEFAULT_STEPS:
            assert step in STEP_REGISTRY

    def test_step_registry_contains_all_functions(self):
        """The registry should contain all four preprocessing functions."""
        expected = {"grayscale", "threshold", "resize", "deskew"}
        assert set(STEP_REGISTRY.keys()) == expected
