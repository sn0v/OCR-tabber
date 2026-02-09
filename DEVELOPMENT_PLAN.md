# OCR-tabber AI Agent Development Plan

This document outlines the prioritized fixes, improvements, and features identified during a comprehensive codebase audit.

## Audit Summary

- **Project Age**: ~11 years (last commit Dec 2014)
- **Python Version**: ~~Python 2 (EOL since 2020)~~ → **Python 3.14.2** ✅
- **Test Coverage**: ~~0%~~ → **113 tests across 7 test modules** ✅
- **Dependencies**: Poetry-managed (`pytesseract`, `Pillow`; dev: `pytest`, `ruff`)
- **Status**: ~~Proof-of-concept needing significant modernization~~ → **Modernized, functional CLI tool with full subcommand interface**

---

## Part 1: Fixes & Improvements (Priority Order)

### CRITICAL PRIORITY

| # | Issue | Status | Evidence |
|---|-------|--------|----------|
| 1 | **Python 2 → 3 Migration** | ✅ Done | `.python-version` = 3.14.2; `pyproject.toml` requires `^3.14`; uses `list[str] \| None` union syntax |
| 2 | **Create requirements.txt** | ✅ Done | Poetry with `pyproject.toml`; deps: `pytesseract ^0.3.10`, `pillow ^11.0.0` |
| 3 | **Replace deprecated `tesseract` module** | ✅ Done | `ocr_tab.py` imports and uses `pytesseract`; configures `--tessdata-dir`, `--psm 6`, char whitelist |
| 4 | **Add error handling to all file I/O** | ✅ Done | Every file op in `ocr_tab.py`, `chord_recognizer.py`, `tab_db_extractor.py`, `cli.py` wrapped in try/except with `FileNotFoundError`, `OSError`, `ValueError`, `RuntimeError` |
| 5 | **Fix hardcoded relative paths** | ✅ Done | All modules use `Path(__file__).parent.parent.parent / "data"` for `DATA_DIR` |

### HIGH PRIORITY

| # | Issue | Status | Evidence |
|---|-------|--------|----------|
| 6 | **Fix performance: DB loaded per chord** | ✅ Done | `cli.py:cmd_recognize()` calls `load_chord_database()` once, passes `chord_db` to `find_and_recognize_chords()` |
| 7 | **Add input validation** | ✅ Done | `validate_image_path()` checks existence + extension against `SUPPORTED_IMAGE_EXTENSIONS`; `parse_tab_file()` validates key count and content |
| 8 | **Add basic test suite** | ✅ Done | 113 tests across 7 modules: `test_chord_recognizer.py`, `test_ocr_tab.py`, `test_tab_db_extractor.py`, `test_batch.py`, `test_formatters.py`, `test_preprocessing.py`; shared `conftest.py` with fixtures |
| 9 | **Add logging framework** | ❌ Not done | Zero `import logging` in codebase; 22 `print()` calls across all 4 source files used for output and error reporting |
| 10 | **Create setup.py/pyproject.toml** | ✅ Done | Full `pyproject.toml` with Poetry build system, `[tool.poetry.scripts]` entrypoint `ocr-tabber = "ocr_tabber.cli:main"` |

### MEDIUM PRIORITY

| # | Issue | Status | Evidence |
|---|-------|--------|----------|
| 11 | **Remove unused imports** | ✅ Done | All imports in source files are actively used; ruff `F` (pyflakes) rules enforce this |
| 12 | **Remove commented-out debug code** | ✅ Done | No commented-out code blocks in any source file |
| 13 | **Add type hints** | ✅ Done | Type aliases (`ChordEntry`, `ChordDatabase`, `NotePosition`, `StringTuning`); all function signatures annotated with return types and parameter types |
| 14 | **Add docstrings** | ✅ Done | All public functions have docstrings with Args/Returns/Raises sections; module-level comments present |
| 15 | **Add linting config** | ✅ Done | Ruff in `pyproject.toml`: rules E, W, F, I, B, C4, UP; `target-version = "py313"`; line-length 100 |
| 16 | **Replace pickle with JSON for chord DB** | ✅ Done | `tab_db_extractor.py` uses `json.dump()`; `chord_recognizer.py` uses `json.load()`; `mainDB.json` is the active database format |

### LOW PRIORITY

| # | Issue | Status | Evidence |
|---|-------|--------|----------|
| 17 | **Refactor variable naming** | ✅ Done | snake_case throughout; descriptive names like `chord_list`, `all_notes`, `string_count` |
| 18 | **Add .editorconfig** | ✅ Done | `.editorconfig` with UTF-8, LF, 4-space Python, 2-space YAML/JSON/TOML |
| 19 | **Add CI/CD pipeline** | ❌ Not done | No `.github/` directory or any CI config files exist |
| 20 | **Create Dockerfile** | ❌ Not done | No `Dockerfile` exists in the project |
| 21 | **Expand README** | ✅ Done | `README.md` has Setup (brew + poetry), Usage (3 CLI commands with examples), License section |

---

## Part 2: New Features (Priority Order)

### HIGH VALUE FEATURES

| # | Feature | Status | Evidence |
|---|---------|--------|----------|
| 1 | **CLI Interface with argparse** | ✅ Done | `cli.py`: `create_parser()` with 4 subcommands (`ocr`, `recognize`, `batch`, `build-db`); `--version`, `-o/--output`, `-f/--format`, `-t/--tab-file`, `--no-preprocess` flags; proper exit codes (0/1) |
| 2 | **Batch processing mode** | ✅ Done | `batch` subcommand accepts directories, globs, multiple files; `--output-dir`, `--recognize` flags; `collect_image_paths()` + `batch_ocr_images()` in `ocr_tab.py` |
| 3 | **Output format options** | ✅ Done | `-f/--format` flag on `ocr` and `recognize` subcommands; `text`, `json`, `csv` formats; `formatters.py` module with separate OCR and chord formatters |
| 4 | **Confidence scoring** | ❌ Not done | Uses `pytesseract.image_to_string()` which returns plain text; no call to `image_to_data()` or confidence extraction |
| 5 | **Config file support** | ❌ Not done | No config file loading, no `--config` flag, no environment variable support |

### MEDIUM VALUE FEATURES

| # | Feature | Status | Evidence |
|---|---------|--------|----------|
| 6 | **Web API** | ❌ Not done | No web framework dependency; no API endpoints |
| 7 | **Pre-processing pipeline** | ✅ Done | `preprocessing.py` with grayscale, threshold, resize, deskew steps; integrated into `ocr_tab_image()` with `--no-preprocess` CLI flag |
| 8 | **Support for bass tabs** | ❌ Not done | `parse_tab_file()` raises `ValueError` for more than 6 strings; hardcoded 6-string assumption |
| 9 | **Chord diagram generator** | ❌ Not done | No SVG/PNG generation; output is text only |
| 10 | **Alternative tuning support** | ❌ Not done | `ALLOWED_KEY` covers note letters A-G but tuning is read from the tab file, not configurable; standard tuning assumed in chord DB matching |

### NICE-TO-HAVE FEATURES

| # | Feature | Status | Evidence |
|---|---------|--------|----------|
| 11 | **MIDI export** | ❌ Not done | No MIDI library; no audio-related dependencies |
| 12 | **Audio playback preview** | ❌ Not done | No audio dependencies |
| 13 | **GUI application** | ❌ Not done | CLI only; see FEATURE_PLAN.md for GUI design considerations |
| 14 | **Real-time camera OCR** | ❌ Not done | No camera/video capture code |
| 15 | **Machine learning OCR model** | ❌ Not done | Uses Tesseract only; no ML training code |
| 16 | **Tab correction suggestions** | ❌ Not done | No suggestion/correction mechanism |
| 17 | **Multi-page PDF support** | ❌ Not done | `validate_image_path()` rejects `.pdf`; only raster image formats supported |
| 18 | **Integration with tab databases** | ❌ Not done | No external API integration |

---

## Progress Summary

### Completed Phases

#### Phase 1 - Make It Work (Critical): COMPLETE
All 5 items done. Python 3.14, Poetry, pytesseract, error handling, pathlib paths.

#### Phase 2 - Make It Testable (High): 4/5 COMPLETE
Done: DB performance fix, input validation, 113-test suite, pyproject.toml.
Remaining: logging framework (still using print statements throughout).

#### Phase 3 - Make It Usable (Features): 3/5 COMPLETE
Done: Full CLI with argparse (4 subcommands), batch processing, output format options (text/json/csv).
Remaining: confidence scoring, config file support.

#### Phase 4 - Make It Professional (Polish): 4/5 COMPLETE
Done: type hints, docstrings, ruff linting, .editorconfig, pickle→JSON migration.
Remaining: CI/CD pipeline, Dockerfile.

#### Phase 5 - Expand Capabilities (Future): 1 FEATURE COMPLETE
Done: Image preprocessing pipeline (grayscale, threshold, resize, deskew).
Remaining: web API, bass tabs, chord diagrams, alternative tunings, and nice-to-have features.

---

## Remaining Work

### Quick Wins (Low Effort)
- [x] Add `.editorconfig`
- [x] Replace pickle with JSON for chord DB

### Medium Effort
- [ ] Add logging framework (replace print statements across source files)
- [ ] Add CI/CD pipeline (GitHub Actions for pytest + ruff)
- [x] Batch processing mode (`batch` subcommand with directory/glob/multi-file support)
- [x] Output format options (`-f text|json|csv` on `ocr` and `recognize` subcommands)

### Larger Efforts
- [ ] Create Dockerfile (needs Tesseract + Python 3.14 base image)
- [x] Image preprocessing pipeline (Pillow-based grayscale, threshold, resize, deskew)
- [ ] Confidence scoring (switch to `pytesseract.image_to_data()`)
- [ ] GUI application (see FEATURE_PLAN.md for toolkit decisions)

---

## Current Architecture

```
src/ocr_tabber/
├── __init__.py         # Package init, __version__ = "0.1.0"
├── cli.py              # CLI entrypoint with argparse (4 subcommands: ocr, recognize, batch, build-db)
├── ocr_tab.py          # OCR processing with pytesseract + Pillow (validates image, configures tesseract)
├── chord_recognizer.py # Chord matching against JSON database (loads DB, parses tab, matches chords)
├── formatters.py       # Output formatters (text, json, csv) for OCR and chord results
├── preprocessing.py    # Image preprocessing pipeline (grayscale, threshold, resize, deskew)
└── tab_db_extractor.py # XML → JSON database builder (parses Gnome Guitar XML, saves .json)

data/
├── mainDB.xml          # Source chord database (512 chords, Gnome Guitar format)
├── mainDB.json         # Compiled chord database (JSON format, 512 chords)
├── testDB.xml          # Small test chord database (2 chords: A Major, C Major)
├── ASCIItab.txt        # Sample ASCII tab (6-line, 4 chords)
└── tessdata/           # Tesseract language data (eng.traineddata + configs)

tests/
├── conftest.py             # Shared fixtures (data_dir, temp_dir, sample_tab_content, sample_xml_content)
├── test_batch.py            # 33 tests: batch collection, OCR, CLI, parser integration
├── test_chord_recognizer.py # 8 tests: DB loading, tab parsing, key validation
├── test_formatters.py       # 27 tests: text/json/csv formatters for OCR and chord results
├── test_ocr_tab.py          # 10 tests: image validation, extension checks
├── test_preprocessing.py    # 24 tests: grayscale, threshold, resize, deskew, pipeline
└── test_tab_db_extractor.py # 11 tests: XML parsing, JSON save/load, error cases

pyproject.toml          # Poetry config, ruff config, pytest config
.python-version         # 3.14.2
.editorconfig           # Editor config (UTF-8, LF, 4-space Python, 2-space YAML/JSON/TOML)
.gitignore              # Ignores test dirs, __pycache__, build artifacts, .venv, poetry.lock
```

---

*Generated: January 2026*
*Last updated: February 2026 -- batch processing, output formats, preprocessing, pickle→JSON, .editorconfig*
