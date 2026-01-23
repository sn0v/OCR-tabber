# OCR-tabber AI Agent Development Plan

This document outlines the prioritized fixes, improvements, and features identified during a comprehensive codebase audit.

## Audit Summary

- **Project Age**: ~11 years (last commit Dec 2014)
- **Python Version**: ~~Python 2 (EOL since 2020)~~ → **Python 3.14** ✅
- **Test Coverage**: ~~0%~~ → **29 tests passing** ✅
- **Status**: ~~Proof-of-concept needing significant modernization~~ → **Modernized, functional CLI tool**

---

## Part 1: Fixes & Improvements (Priority Order)

### 🔴 CRITICAL PRIORITY

| # | Issue | Status |
|---|-------|--------|
| 1 | **Python 2 → 3 Migration** | ✅ Done - Using Python 3.14 with modern syntax |
| 2 | **Create requirements.txt** | ✅ Done - Using Poetry with `pyproject.toml` |
| 3 | **Replace deprecated `tesseract` module** | ✅ Done - Using `pytesseract` |
| 4 | **Add error handling to all file I/O** | ✅ Done - All operations have try/except with proper error messages |
| 5 | **Fix hardcoded relative paths** | ✅ Done - Using `pathlib` relative to module location |

### 🟠 HIGH PRIORITY

| # | Issue | Status |
|---|-------|--------|
| 6 | **Fix performance: DB loaded per chord** | ✅ Done - DB loaded once in main, passed to functions |
| 7 | **Add input validation** | ✅ Done - Validates image extensions, tab file content |
| 8 | **Add basic test suite** | ✅ Done - 29 tests in `tests/` directory |
| 9 | **Add logging framework** | ⏳ Pending - Still uses print statements |
| 10 | **Create setup.py/pyproject.toml** | ✅ Done - Full Poetry setup with CLI entrypoint |

### 🟡 MEDIUM PRIORITY

| # | Issue | Status |
|---|-------|--------|
| 11 | **Remove unused imports** | ✅ Done - Cleaned up |
| 12 | **Remove commented-out debug code** | ✅ Done - Code is clean |
| 13 | **Add type hints** | ✅ Done - Type aliases and annotations added |
| 14 | **Add docstrings** | ✅ Done - All functions documented |
| 15 | **Add linting config** | ✅ Done - Ruff configured in `pyproject.toml` |
| 16 | **Replace pickle with JSON for chord DB** | ⏳ Pending |

### 🟢 LOW PRIORITY

| # | Issue | Status |
|---|-------|--------|
| 17 | **Refactor variable naming** | ✅ Done - Modern Python naming conventions |
| 18 | **Add .editorconfig** | ⏳ Pending |
| 19 | **Add CI/CD pipeline** | ⏳ Pending |
| 20 | **Create Dockerfile** | ⏳ Pending |
| 21 | **Expand README** | ✅ Done - Setup and usage examples added |

---

## Part 2: New Features (Priority Order)

### 🔴 HIGH VALUE FEATURES

| # | Feature | Status |
|---|---------|--------|
| 1 | **CLI Interface with argparse** | ✅ Done - Full CLI with subcommands (`ocr`, `recognize`, `build-db`) |
| 2 | **Batch processing mode** | ⏳ Pending |
| 3 | **Output format options** | ⏳ Pending |
| 4 | **Confidence scoring** | ⏳ Pending |
| 5 | **Config file support** | ⏳ Pending |

### 🟠 MEDIUM VALUE FEATURES

| # | Feature | Status |
|---|---------|--------|
| 6 | **Web API** | ⏳ Pending |
| 7 | **Pre-processing pipeline** | ⏳ Pending |
| 8 | **Support for bass tabs** | ⏳ Pending |
| 9 | **Chord diagram generator** | ⏳ Pending |
| 10 | **Alternative tuning support** | ⏳ Pending |

### 🟡 NICE-TO-HAVE FEATURES

| # | Feature | Status |
|---|---------|--------|
| 11 | **MIDI export** | ⏳ Pending |
| 12 | **Audio playback preview** | ⏳ Pending |
| 13 | **GUI application** | ⏳ Pending - See FEATURE_PLAN.md for details |
| 14 | **Real-time camera OCR** | ⏳ Pending |
| 15 | **Machine learning OCR model** | ⏳ Pending |
| 16 | **Tab correction suggestions** | ⏳ Pending |
| 17 | **Multi-page PDF support** | ⏳ Pending |
| 18 | **Integration with tab databases** | ⏳ Pending |

---

## Progress Summary

### Completed Phases

#### ✅ Phase 1 - Make It Work (Critical)
All 5 items complete.

#### ✅ Phase 2 - Make It Testable (High)
4 of 5 items complete. Remaining: logging framework.

#### 🔄 Phase 3 - Make It Usable (Features)
1 of 4 items complete (CLI with argparse).

#### 🔄 Phase 4 - Make It Professional (Polish)
3 of 5 items complete (type hints, docstrings, linting config). Remaining: CI/CD, Dockerfile.

#### ⏳ Phase 5 - Expand Capabilities (Future)
Not started.

---

## Remaining Work

### Quick Wins (Low Effort)
- [ ] Add `.editorconfig`
- [ ] Replace pickle with JSON for chord DB

### Medium Effort
- [ ] Add logging framework (replace print statements)
- [ ] Add CI/CD pipeline (GitHub Actions)
- [ ] Batch processing mode
- [ ] Output format options

### Larger Efforts
- [ ] Create Dockerfile
- [ ] Image preprocessing pipeline
- [ ] GUI application (see FEATURE_PLAN.md)

---

## Current Architecture

```
src/ocr_tabber/
├── cli.py              # CLI entrypoint with argparse
├── ocr_tab.py          # OCR processing with pytesseract
├── chord_recognizer.py # Chord matching against database
└── tab_db_extractor.py # XML → pickle database builder

data/
├── mainDB.xml          # Source chord database (512 chords)
├── mainDB.pkl          # Compiled chord database
├── ASCIItab.txt        # Sample ASCII tab
└── tessdata/           # Tesseract language data

tests/
├── test_chord_recognizer.py
├── test_ocr_tab.py
└── test_tab_db_extractor.py
```

---

*Generated: January 2026*
*Last updated: January 2026*
