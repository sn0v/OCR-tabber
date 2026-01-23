"""Tests for the ocr_tab module."""

from pathlib import Path

import pytest

from ocr_tabber.ocr_tab import (
    SUPPORTED_IMAGE_EXTENSIONS,
    validate_image_path,
)


class TestValidateImagePath:
    """Tests for validate_image_path function."""

    def test_validate_existing_png(self, temp_dir: Path):
        """Test validation of existing PNG file."""
        png_file = temp_dir / "test.png"
        png_file.write_bytes(b"fake png content")

        result = validate_image_path(str(png_file))
        assert result == png_file

    def test_validate_existing_jpg(self, temp_dir: Path):
        """Test validation of existing JPG file."""
        jpg_file = temp_dir / "test.jpg"
        jpg_file.write_bytes(b"fake jpg content")

        result = validate_image_path(str(jpg_file))
        assert result == jpg_file

    def test_validate_existing_jpeg(self, temp_dir: Path):
        """Test validation of existing JPEG file."""
        jpeg_file = temp_dir / "test.jpeg"
        jpeg_file.write_bytes(b"fake jpeg content")

        result = validate_image_path(str(jpeg_file))
        assert result == jpeg_file

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

    def test_validate_unsupported_extension(self, temp_dir: Path):
        """Test that ValueError is raised for unsupported extensions."""
        txt_file = temp_dir / "test.txt"
        txt_file.write_text("not an image")

        with pytest.raises(ValueError, match="Unsupported image format"):
            validate_image_path(str(txt_file))

    def test_validate_pdf_not_supported(self, temp_dir: Path):
        """Test that PDF files are not supported."""
        pdf_file = temp_dir / "test.pdf"
        pdf_file.write_bytes(b"fake pdf content")

        with pytest.raises(ValueError, match="Unsupported image format"):
            validate_image_path(str(pdf_file))

    def test_validate_no_extension(self, temp_dir: Path):
        """Test that files without extension are rejected."""
        no_ext_file = temp_dir / "noextension"
        no_ext_file.write_bytes(b"content")

        with pytest.raises(ValueError, match="Unsupported image format"):
            validate_image_path(str(no_ext_file))


class TestSupportedImageExtensions:
    """Tests for the SUPPORTED_IMAGE_EXTENSIONS constant."""

    def test_common_formats_supported(self):
        """Test that common image formats are in supported list."""
        common_formats = ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
        for fmt in common_formats:
            assert fmt in SUPPORTED_IMAGE_EXTENSIONS

    def test_extensions_are_lowercase(self):
        """Test that all extensions are lowercase."""
        for ext in SUPPORTED_IMAGE_EXTENSIONS:
            assert ext == ext.lower()
            assert ext.startswith('.')
