"""Tests for the ocr_tab module."""

from pathlib import Path

import pytest

from ocr_tabber.ocr_tab import (
    SUPPORTED_IMAGE_EXTENSIONS,
    validate_image_path,
)


class TestValidateImagePath:
    """Tests for validate_image_path function."""

    @pytest.mark.parametrize("extension", [".png", ".jpg", ".jpeg", ".gif", ".bmp"])
    def test_validate_supported_extensions(self, temp_dir: Path, extension: str):
        """Test validation accepts supported image extensions."""
        img_file = temp_dir / f"test{extension}"
        img_file.write_bytes(b"fake image content")

        result = validate_image_path(str(img_file))
        assert result == img_file

    def test_validate_case_insensitive_extension(self, temp_dir: Path):
        """Test that extension validation is case-insensitive."""
        png_file = temp_dir / "test.PNG"
        png_file.write_bytes(b"fake png content")

        result = validate_image_path(str(png_file))
        assert result == png_file

    def test_validate_nonexistent_file(self, temp_dir: Path):
        """Test that FileNotFoundError is raised for missing files."""
        with pytest.raises(FileNotFoundError, match="Image file not found"):
            validate_image_path(str(temp_dir / "nonexistent.png"))

    @pytest.mark.parametrize("filename", ["test.txt", "test.pdf", "noextension"])
    def test_validate_rejects_unsupported_formats(self, temp_dir: Path, filename: str):
        """Test that ValueError is raised for unsupported file formats."""
        invalid_file = temp_dir / filename
        invalid_file.write_bytes(b"not an image")

        with pytest.raises(ValueError, match="Unsupported image format"):
            validate_image_path(str(invalid_file))


class TestSupportedImageExtensions:
    """Tests for the SUPPORTED_IMAGE_EXTENSIONS constant."""

    def test_supported_extensions_format(self):
        """Test that supported extensions are properly formatted and include common formats."""
        common_formats = ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
        for fmt in common_formats:
            assert fmt in SUPPORTED_IMAGE_EXTENSIONS

        for ext in SUPPORTED_IMAGE_EXTENSIONS:
            assert ext == ext.lower()
            assert ext.startswith('.')
