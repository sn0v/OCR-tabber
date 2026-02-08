# OCR-tabber AI Agent Development Plan

This document outlines the prioritized fixes, improvements, and features identified during a comprehensive codebase audit.

## Audit Summary

- **Project Age**: ~11 years (last commit Dec 2014)
- **Python Version**: ~~Python 2 (EOL since 2020)~~ → **Python 3.14.2** ✅
- **Test Coverage**: ~~0%~~ → **29 tests across 3 test modules** ✅
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
| 8 | **Add basic test suite** | ✅ Done | 29 tests: `test_chord_recognizer.py` (8), `test_ocr_tab.py` (10 incl. parametrize), `test_tab_db_extractor.py` (9 + 2 save); shared `conftest.py` with fixtures |
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
| 16 | **Replace pickle with JSON for chord DB** | ❌ Not done | `tab_db_extractor.py` still uses `pickle.dump()`; `chord_recognizer.py` still uses `pickle.load()`; `mainDB.pkl` is the active database format |

### LOW PRIORITY

| # | Issue | Status | Evidence |
|---|-------|--------|----------|
| 17 | **Refactor variable naming** | ✅ Done | snake_case throughout; descriptive names like `chord_list`, `all_notes`, `string_count` |
| 18 | **Add .editorconfig** | ❌ Not done | No `.editorconfig` file exists in the project |
| 19 | **Add CI/CD pipeline** | ❌ Not done | No `.github/` directory or any CI config files exist |
| 20 | **Create Dockerfile** | ❌ Not done | No `Dockerfile` exists in the project |
| 21 | **Expand README** | ✅ Done | `README.md` has Setup (brew + poetry), Usage (3 CLI commands with examples), License section |

---

## Part 2: New Features (Priority Order)

### HIGH VALUE FEATURES

| # | Feature | Status | Evidence |
|---|---------|--------|----------|
| 1 | **CLI Interface with argparse** | ✅ Done | `cli.py`: 146 lines; `create_parser()` with 3 subcommands (`ocr`, `recognize`, `build-db`); `--version`, `-o/--output`, `-t/--tab-file` flags; proper exit codes (0/1) |
| 2 | **Batch processing mode** | ❌ Not done | `cmd_ocr()` accepts single `args.image` only; no directory/glob support |
| 3 | **Output format options** | ❌ Not done | Output is always plain text to stdout or single file via `-o`; no JSON/XML/MusicXML options |
| 4 | **Confidence scoring** | ❌ Not done | Uses `pytesseract.image_to_string()` which returns plain text; no call to `image_to_data()` or confidence extraction |
| 5 | **Config file support** | ❌ Not done | No config file loading, no `--config` flag, no environment variable support |

### MEDIUM VALUE FEATURES

| # | Feature | Status | Evidence |
|---|---------|--------|----------|
| 6 | **Web API** | ❌ Not done | No web framework dependency; no API endpoints |
| 7 | **Pre-processing pipeline** | ❌ Not done | `ocr_tab.py` passes image directly to tesseract; no deskew, contrast, or noise removal |
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
Done: DB performance fix, input validation, 29-test suite, pyproject.toml.
Remaining: logging framework (still using print statements throughout).

#### Phase 3 - Make It Usable (Features): 1/5 COMPLETE
Done: Full CLI with argparse (3 subcommands, flags, version, exit codes).
Remaining: batch processing, output formats, confidence scoring, config file support.

#### Phase 4 - Make It Professional (Polish): 3/5 COMPLETE
Done: type hints (aliases + annotations), docstrings (Args/Returns/Raises), ruff linting.
Remaining: CI/CD pipeline, Dockerfile.

#### Phase 5 - Expand Capabilities (Future): NOT STARTED
No medium-value or nice-to-have features have been implemented.

---

## Remaining Work

### Quick Wins (Low Effort)
- [ ] Add `.editorconfig`
- [ ] Replace pickle with JSON for chord DB (change `tab_db_extractor.py` and `chord_recognizer.py`)

### Medium Effort
- [ ] Add logging framework (replace 22 `print()` calls across 4 source files)
- [ ] Add CI/CD pipeline (GitHub Actions for pytest + ruff)
- [ ] Batch processing mode (accept directory or glob pattern in `cmd_ocr`)
- [ ] Output format options (add `--format` flag: text, json, musicxml)

### Larger Efforts
- [ ] Create Dockerfile (needs Tesseract + Python 3.14 base image)
- [ ] Image preprocessing pipeline (Pillow-based deskew, contrast, denoise)
- [ ] Confidence scoring (switch to `pytesseract.image_to_data()`)
- [ ] GUI application (see FEATURE_PLAN.md for toolkit decisions)

---

## Current Architecture

```
src/ocr_tabber/
├── __init__.py         # Package init, __version__ = "0.1.0"
├── cli.py              # CLI entrypoint with argparse (3 subcommands: ocr, recognize, build-db)
├── ocr_tab.py          # OCR processing with pytesseract + Pillow (validates image, configures tesseract)
├── chord_recognizer.py # Chord matching against pickle database (loads DB, parses tab, matches chords)
└── tab_db_extractor.py # XML → pickle database builder (parses Gnome Guitar XML, saves .pkl)

data/
├── mainDB.xml          # Source chord database (512 chords, Gnome Guitar format)
├── mainDB.pkl          # Compiled chord database (pickle format)
├── testDB.xml          # Small test chord database (2 chords: A Major, C Major)
├── ASCIItab.txt        # Sample ASCII tab (6-line, 4 chords)
└── tessdata/           # Tesseract language data (eng.traineddata + configs)

tests/
├── conftest.py             # Shared fixtures (data_dir, temp_dir, sample_tab_content, sample_xml_content)
├── test_chord_recognizer.py # 8 tests: DB loading, tab parsing, key validation
├── test_ocr_tab.py          # 10 tests: image validation, extension checks
└── test_tab_db_extractor.py # 11 tests: XML parsing, pickle save/load, error cases

pyproject.toml          # Poetry config, ruff config, pytest config
.python-version         # 3.14.2
.gitignore              # Ignores test dirs, __pycache__, build artifacts, .venv, poetry.lock
```

---

*Generated: January 2026*
*Last updated: February 2026 -- verified against actual source code*
