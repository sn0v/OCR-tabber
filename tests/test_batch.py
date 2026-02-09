"""Tests for batch processing functionality."""

from pathlib import Path
from unittest.mock import patch

import pytest

from ocr_tabber.cli import cmd_batch, create_parser, main
from ocr_tabber.ocr_tab import (
    SUPPORTED_IMAGE_EXTENSIONS,
    batch_ocr_images,
    collect_image_paths,
)


class TestCollectImagePaths:
    """Tests for collect_image_paths function."""

    def test_collect_from_directory(self, temp_dir: Path):
        """Test collecting image files from a directory."""
        # Create some image files and a non-image file
        (temp_dir / "tab1.png").write_bytes(b"fake png")
        (temp_dir / "tab2.jpg").write_bytes(b"fake jpg")
        (temp_dir / "notes.txt").write_text("not an image")

        result = collect_image_paths(str(temp_dir))

        assert len(result) == 2
        filenames = {p.name for p in result}
        assert filenames == {"tab1.png", "tab2.jpg"}

    def test_collect_from_directory_sorted(self, temp_dir: Path):
        """Test that collected paths are sorted."""
        (temp_dir / "c_tab.png").write_bytes(b"fake")
        (temp_dir / "a_tab.png").write_bytes(b"fake")
        (temp_dir / "b_tab.png").write_bytes(b"fake")

        result = collect_image_paths(str(temp_dir))

        names = [p.name for p in result]
        assert names == sorted(names)

    def test_collect_single_file(self, temp_dir: Path):
        """Test collecting a single image file path."""
        img = temp_dir / "single.png"
        img.write_bytes(b"fake png")

        result = collect_image_paths(str(img))

        assert len(result) == 1
        assert result[0] == img

    def test_collect_single_file_unsupported_format(self, temp_dir: Path):
        """Test that unsupported single file raises ValueError."""
        txt = temp_dir / "notes.txt"
        txt.write_text("not an image")

        with pytest.raises(ValueError, match="Unsupported image format"):
            collect_image_paths(str(txt))

    def test_collect_nonexistent_path(self, temp_dir: Path):
        """Test that nonexistent path raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="Path not found"):
            collect_image_paths(str(temp_dir / "nonexistent"))

    def test_collect_empty_directory(self, temp_dir: Path):
        """Test that empty directory raises ValueError."""
        empty_dir = temp_dir / "empty"
        empty_dir.mkdir()

        with pytest.raises(ValueError, match="No valid image files found"):
            collect_image_paths(str(empty_dir))

    def test_collect_directory_no_images(self, temp_dir: Path):
        """Test directory with files but no images raises ValueError."""
        (temp_dir / "notes.txt").write_text("text file")
        (temp_dir / "data.csv").write_text("csv file")

        with pytest.raises(ValueError, match="No valid image files found"):
            collect_image_paths(str(temp_dir))

    def test_collect_glob_pattern(self, temp_dir: Path):
        """Test collecting files via a glob pattern."""
        (temp_dir / "tab1.png").write_bytes(b"fake")
        (temp_dir / "tab2.png").write_bytes(b"fake")
        (temp_dir / "tab3.jpg").write_bytes(b"fake")

        # Use a glob pattern relative to the temp dir
        pattern = str(temp_dir / "*.png")
        result = collect_image_paths(pattern)

        assert len(result) == 2
        assert all(p.suffix == ".png" for p in result)

    def test_collect_glob_no_matches(self, temp_dir: Path):
        """Test that glob pattern with no matches raises ValueError."""
        pattern = str(temp_dir / "*.png")

        with pytest.raises(ValueError, match="No valid image files found"):
            collect_image_paths(pattern)

    def test_collect_all_supported_extensions(self, temp_dir: Path):
        """Test that all supported extensions are collected."""
        for ext in SUPPORTED_IMAGE_EXTENSIONS:
            (temp_dir / f"test{ext}").write_bytes(b"fake")

        result = collect_image_paths(str(temp_dir))

        assert len(result) == len(SUPPORTED_IMAGE_EXTENSIONS)


class TestBatchOcrImages:
    """Tests for batch_ocr_images function."""

    @patch("ocr_tabber.ocr_tab.ocr_tab_image")
    def test_batch_with_directory(self, mock_ocr, temp_dir: Path):
        """Test batch processing a directory of images."""
        (temp_dir / "img1.png").write_bytes(b"fake")
        (temp_dir / "img2.png").write_bytes(b"fake")
        mock_ocr.return_value = "e|---\nB|---\n"

        results = batch_ocr_images([str(temp_dir)])

        assert len(results) == 2
        assert all(r['error'] is None for r in results)
        assert all(r['result'] == "e|---\nB|---\n" for r in results)

    @patch("ocr_tabber.ocr_tab.ocr_tab_image")
    def test_batch_with_multiple_sources(self, mock_ocr, temp_dir: Path):
        """Test batch processing with multiple source paths."""
        dir1 = temp_dir / "dir1"
        dir2 = temp_dir / "dir2"
        dir1.mkdir()
        dir2.mkdir()
        (dir1 / "a.png").write_bytes(b"fake")
        (dir2 / "b.png").write_bytes(b"fake")
        mock_ocr.return_value = "tab text"

        results = batch_ocr_images([str(dir1), str(dir2)])

        assert len(results) == 2
        assert all(r['error'] is None for r in results)

    @patch("ocr_tabber.ocr_tab.ocr_tab_image")
    def test_batch_handles_ocr_error_gracefully(self, mock_ocr, temp_dir: Path):
        """Test that OCR errors on individual files don't stop processing."""
        (temp_dir / "good.png").write_bytes(b"fake")
        (temp_dir / "bad.png").write_bytes(b"fake")

        def side_effect(path, **kwargs):
            if "bad" in path:
                raise RuntimeError("OCR failed for this image")
            return "ocr result"

        mock_ocr.side_effect = side_effect

        results = batch_ocr_images([str(temp_dir)])

        assert len(results) == 2
        successes = [r for r in results if r['error'] is None]
        failures = [r for r in results if r['error'] is not None]
        assert len(successes) == 1
        assert len(failures) == 1
        assert "OCR failed" in failures[0]['error']

    def test_batch_with_nonexistent_source(self, temp_dir: Path):
        """Test that nonexistent source is recorded as an error."""
        results = batch_ocr_images([str(temp_dir / "nonexistent")])

        assert len(results) == 1
        assert results[0]['error'] is not None
        assert results[0]['result'] is None

    @patch("ocr_tabber.ocr_tab.ocr_tab_image")
    def test_batch_mixed_valid_and_invalid_sources(self, mock_ocr, temp_dir: Path):
        """Test batch with both valid and invalid sources."""
        (temp_dir / "good.png").write_bytes(b"fake")
        mock_ocr.return_value = "tab text"

        results = batch_ocr_images([
            str(temp_dir),
            str(temp_dir / "nonexistent"),
        ])

        # One success from the directory, one error from the nonexistent path
        assert len(results) == 2
        successes = [r for r in results if r['error'] is None]
        failures = [r for r in results if r['error'] is not None]
        assert len(successes) == 1
        assert len(failures) == 1

    def test_batch_empty_sources(self):
        """Test batch with empty source list returns empty results."""
        results = batch_ocr_images([])
        assert results == []

    @patch("ocr_tabber.ocr_tab.ocr_tab_image")
    def test_batch_single_file_source(self, mock_ocr, temp_dir: Path):
        """Test batch processing a single file path."""
        img = temp_dir / "single.png"
        img.write_bytes(b"fake")
        mock_ocr.return_value = "single result"

        results = batch_ocr_images([str(img)])

        assert len(results) == 1
        assert results[0]['result'] == "single result"
        assert results[0]['error'] is None


class TestCmdBatch:
    """Tests for the cmd_batch CLI function."""

    @patch("ocr_tabber.cli.batch_ocr_images")
    def test_batch_basic_output(self, mock_batch, temp_dir: Path, capsys):
        """Test that batch command prints results summary."""
        mock_batch.return_value = [
            {'file': '/tmp/img1.png', 'result': 'text1', 'error': None},
            {'file': '/tmp/img2.png', 'result': 'text2', 'error': None},
        ]

        parser = create_parser()
        args = parser.parse_args(["batch", str(temp_dir)])
        result = cmd_batch(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "[OK]" in captured.out
        assert "2/2 succeeded" in captured.out
        assert "0/2 failed" in captured.out

    @patch("ocr_tabber.cli.batch_ocr_images")
    def test_batch_with_errors_returns_nonzero(self, mock_batch, temp_dir: Path, capsys):
        """Test that batch command returns 1 when there are errors."""
        mock_batch.return_value = [
            {'file': '/tmp/img1.png', 'result': 'text1', 'error': None},
            {'file': '/tmp/bad.png', 'result': None, 'error': 'OCR failed'},
        ]

        parser = create_parser()
        args = parser.parse_args(["batch", str(temp_dir)])
        result = cmd_batch(args)

        assert result == 1
        captured = capsys.readouterr()
        assert "[FAIL]" in captured.err
        assert "1/2 succeeded" in captured.out
        assert "1/2 failed" in captured.out

    @patch("ocr_tabber.cli.batch_ocr_images")
    def test_batch_no_results(self, mock_batch, temp_dir: Path, capsys):
        """Test batch command with no files to process."""
        mock_batch.return_value = []

        parser = create_parser()
        args = parser.parse_args(["batch", str(temp_dir)])
        result = cmd_batch(args)

        assert result == 1
        captured = capsys.readouterr()
        assert "No files to process" in captured.err

    @patch("ocr_tabber.cli.batch_ocr_images")
    def test_batch_output_dir(self, mock_batch, temp_dir: Path, capsys):
        """Test that --output-dir writes individual result files."""
        output_dir = temp_dir / "output"
        mock_batch.return_value = [
            {'file': '/tmp/tab1.png', 'result': 'ocr text 1', 'error': None},
            {'file': '/tmp/tab2.png', 'result': 'ocr text 2', 'error': None},
        ]

        parser = create_parser()
        args = parser.parse_args([
            "batch", str(temp_dir), "-o", str(output_dir),
        ])
        result = cmd_batch(args)

        assert result == 0
        assert output_dir.exists()
        assert (output_dir / "tab1.txt").read_text() == "ocr text 1"
        assert (output_dir / "tab2.txt").read_text() == "ocr text 2"

    @patch("ocr_tabber.cli.batch_ocr_images")
    def test_batch_output_dir_created_automatically(self, mock_batch, temp_dir: Path):
        """Test that output directory is created if it doesn't exist."""
        nested_output = temp_dir / "nested" / "output"
        mock_batch.return_value = [
            {'file': '/tmp/tab.png', 'result': 'text', 'error': None},
        ]

        parser = create_parser()
        args = parser.parse_args([
            "batch", str(temp_dir), "-o", str(nested_output),
        ])
        cmd_batch(args)

        assert nested_output.exists()
        assert nested_output.is_dir()

    @patch("ocr_tabber.cli.batch_ocr_images")
    def test_batch_error_files_not_written(self, mock_batch, temp_dir: Path):
        """Test that failed files are not written to output directory."""
        output_dir = temp_dir / "output"
        mock_batch.return_value = [
            {'file': '/tmp/bad.png', 'result': None, 'error': 'OCR failed'},
        ]

        parser = create_parser()
        args = parser.parse_args([
            "batch", str(temp_dir), "-o", str(output_dir),
        ])
        cmd_batch(args)

        assert output_dir.exists()
        assert not (output_dir / "bad.txt").exists()


class TestBatchParserIntegration:
    """Tests for batch subcommand argument parsing."""

    def test_batch_parser_exists(self):
        """Test that the batch subcommand is registered."""
        parser = create_parser()
        # Should not raise SystemExit for valid batch args
        args = parser.parse_args(["batch", "/some/path"])
        assert args.command == "batch"

    def test_batch_parser_multiple_inputs(self):
        """Test batch accepts multiple input paths."""
        parser = create_parser()
        args = parser.parse_args(["batch", "/path1", "/path2", "/path3"])
        assert args.inputs == ["/path1", "/path2", "/path3"]

    def test_batch_parser_output_dir_flag(self):
        """Test batch --output-dir flag parsing."""
        parser = create_parser()
        args = parser.parse_args(["batch", "/path", "-o", "/output"])
        assert args.output_dir == "/output"

    def test_batch_parser_recognize_flag(self):
        """Test batch --recognize flag parsing."""
        parser = create_parser()
        args = parser.parse_args(["batch", "/path", "-r"])
        assert args.recognize is True

    def test_batch_parser_recognize_default(self):
        """Test that --recognize defaults to False."""
        parser = create_parser()
        args = parser.parse_args(["batch", "/path"])
        assert args.recognize is False

    def test_batch_parser_output_dir_default(self):
        """Test that --output-dir defaults to None."""
        parser = create_parser()
        args = parser.parse_args(["batch", "/path"])
        assert args.output_dir is None

    def test_batch_parser_all_flags(self):
        """Test batch with all flags combined."""
        parser = create_parser()
        args = parser.parse_args([
            "batch", "/dir1", "/dir2",
            "-o", "/output",
            "-r",
        ])
        assert args.inputs == ["/dir1", "/dir2"]
        assert args.output_dir == "/output"
        assert args.recognize is True

    def test_batch_requires_inputs(self):
        """Test that batch requires at least one input."""
        parser = create_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["batch"])


class TestBatchMainEntryPoint:
    """Tests for batch processing via the main() entry point."""

    @patch("ocr_tabber.cli.batch_ocr_images")
    def test_main_batch_invocation(self, mock_batch, temp_dir: Path):
        """Test invoking batch through main()."""
        mock_batch.return_value = [
            {'file': '/tmp/img.png', 'result': 'text', 'error': None},
        ]

        result = main(["batch", str(temp_dir)])
        assert result == 0
        mock_batch.assert_called_once()

    @patch("ocr_tabber.cli.batch_ocr_images")
    def test_main_batch_with_output_dir(self, mock_batch, temp_dir: Path):
        """Test invoking batch with --output-dir through main()."""
        output_dir = temp_dir / "results"
        mock_batch.return_value = [
            {'file': '/tmp/img.png', 'result': 'text', 'error': None},
        ]

        result = main(["batch", str(temp_dir), "-o", str(output_dir)])
        assert result == 0
        assert output_dir.exists()
