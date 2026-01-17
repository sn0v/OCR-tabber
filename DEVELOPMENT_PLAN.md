# OCR-tabber AI Agent Development Plan

This document outlines the prioritized fixes, improvements, and features identified during a comprehensive codebase audit.

## Audit Summary

- **Project Age**: ~11 years (last commit Dec 2014)
- **Python Version**: Python 2 (EOL since 2020)
- **Test Coverage**: 0%
- **Status**: Proof-of-concept needing significant modernization

---

## Part 1: Fixes & Improvements (Priority Order)

### 🔴 CRITICAL PRIORITY

| # | Issue | Files Affected | Effort |
|---|-------|----------------|--------|
| 1 | **Python 2 → 3 Migration** - All print statements use Python 2 syntax. Code will not run on Python 3. | `ocr-tab.py:29-30`, `chord-recognizer.py:55,59` | Low |
| 2 | **Create requirements.txt** - No dependency file exists. Environment cannot be reproduced. | New file | Low |
| 3 | **Replace deprecated `tesseract` module** - Use `pytesseract` instead (original is EOL) | `ocr-tab.py` | Medium |
| 4 | **Add error handling to all file I/O** - All file operations are unguarded; crashes on missing files | All 3 Python files | Medium |
| 5 | **Fix hardcoded relative paths** - Scripts only work from specific directories | `chord-recognizer.py:16,41`, `tabDBextractor.py:11,38`, `ocr-tab.py:14` | Low |

### 🟠 HIGH PRIORITY

| # | Issue | Files Affected | Effort |
|---|-------|----------------|--------|
| 6 | **Fix performance: DB loaded per chord** - `pickle.load()` runs inside a loop on every chord recognition call | `chord-recognizer.py:40-41` | Low |
| 7 | **Add input validation** - No validation on CLI args or file types | `ocr-tab.py:24-27` | Low |
| 8 | **Add basic test suite** - 0% test coverage, `testDB.xml` exists but unused | New `tests/` directory | Medium |
| 9 | **Add logging framework** - Replace print statements with proper logging | All Python files | Medium |
| 10 | **Create setup.py/pyproject.toml** - No package installation mechanism | New file | Low |

### 🟡 MEDIUM PRIORITY

| # | Issue | Files Affected | Effort |
|---|-------|----------------|--------|
| 11 | **Remove unused imports** - `json` imported but never used | `tabDBextractor.py:8` | Trivial |
| 12 | **Remove commented-out debug code** - Clutters readability | `chord-recognizer.py:35-36,48,50-51,82-83` | Trivial |
| 13 | **Add type hints** - No type annotations anywhere | All Python files | Medium |
| 14 | **Add docstrings** - No function/module documentation | All Python files | Medium |
| 15 | **Add linting config** - No `.flake8`, `.pylintrc`, or `pyproject.toml` linting | New config files | Low |
| 16 | **Replace pickle with JSON for chord DB** - Pickle is unsafe for untrusted data | `chord-recognizer.py`, `tabDBextractor.py` | Medium |

### 🟢 LOW PRIORITY

| # | Issue | Files Affected | Effort |
|---|-------|----------------|--------|
| 17 | **Refactor variable naming** - Hungarian notation (`mImgFile`) is outdated | `ocr-tab.py` | Low |
| 18 | **Add .editorconfig** - No code style enforcement | New file | Trivial |
| 19 | **Add CI/CD pipeline** - No GitHub Actions or automation | New `.github/workflows/` | Medium |
| 20 | **Create Dockerfile** - No containerization for reproducible deployment | New file | Medium |
| 21 | **Expand README** - Only 12 lines, no usage examples | `README.md` | Low |

---

## Part 2: New Features (Priority Order)

### 🔴 HIGH VALUE FEATURES

| # | Feature | Description | Effort |
|---|---------|-------------|--------|
| 1 | **CLI Interface with argparse** | Replace raw `sys.argv` with proper CLI: `ocr-tab --input image.png --output tab.txt` | Medium |
| 2 | **Batch processing mode** | Process multiple tab images at once: `ocr-tab --dir ./tabs/` | Medium |
| 3 | **Output format options** | Export recognized tabs as: plain text, JSON, MusicXML, or PDF | Medium |
| 4 | **Confidence scoring** | Return confidence level for chord recognition results | Medium |
| 5 | **Config file support** | YAML/TOML config for paths, Tesseract settings, output preferences | Low |

### 🟠 MEDIUM VALUE FEATURES

| # | Feature | Description | Effort |
|---|---------|-------------|--------|
| 6 | **Web API** | Flask/FastAPI REST endpoint: `POST /ocr` with image upload | Medium |
| 7 | **Pre-processing pipeline** | Image enhancement before OCR (contrast, deskew, noise removal) using Pillow/OpenCV | High |
| 8 | **Support for bass tabs** | Extend recognizer for 4-string bass tablature | Medium |
| 9 | **Chord diagram generator** | Output visual chord diagrams (SVG/PNG) alongside text | High |
| 10 | **Alternative tuning support** | Handle Drop D, DADGAD, Open G, etc. | Medium |

### 🟡 NICE-TO-HAVE FEATURES

| # | Feature | Description | Effort |
|---|---------|-------------|--------|
| 11 | **MIDI export** | Convert recognized tabs to MIDI file | High |
| 12 | **Audio playback preview** | Generate audio preview of recognized tab | High |
| 13 | **GUI application** | Tkinter/PyQt desktop app for non-CLI users | High |
| 14 | **Real-time camera OCR** | Use webcam to capture and process tabs live | Very High |
| 15 | **Machine learning OCR model** | Train custom model specifically for guitar tablature | Very High |
| 16 | **Tab correction suggestions** | Suggest alternate fingerings or corrections for impossible chord shapes | Medium |
| 17 | **Multi-page PDF support** | Parse entire songbook PDFs | Medium |
| 18 | **Integration with tab databases** | Fetch/compare against Ultimate Guitar, Songsterr APIs | Medium |

---

## Recommended Implementation Phases

### Phase 1 - Make It Work (Critical)
```
1. Python 3 migration
2. Create requirements.txt
3. Replace tesseract → pytesseract
4. Add error handling
5. Fix path handling
```

### Phase 2 - Make It Testable (High)
```
6. Fix DB loading performance
7. Add input validation
8. Create test suite
9. Add logging
10. Add pyproject.toml
```

### Phase 3 - Make It Usable (Features)
```
11. CLI with argparse
12. Batch processing
13. Output format options
14. Config file support
```

### Phase 4 - Make It Professional (Polish)
```
15. Type hints + docstrings
16. Linting config
17. CI/CD pipeline
18. Dockerfile
19. Expanded README
```

### Phase 5 - Expand Capabilities (Future)
```
20. Web API
21. Pre-processing pipeline
22. Additional features as needed
```

---

## Key Technical Debt Details

### Critical Issues Found

1. **Python 2 Syntax** - Print statements without parentheses:
   ```python
   # Current (fails on Python 3)
   print "OCRed tab -"

   # Should be
   print("OCRed tab -")
   ```

2. **No Error Handling** - All file operations are unguarded:
   ```python
   # Current (crashes on missing file)
   mBuffer = open(mImgFile, "rb").read()

   # Should have try/except
   ```

3. **Performance Issue** - Database loaded on every chord:
   ```python
   # Current (inside loop, called per chord)
   def chordRecognition(key, chordNotes):
       with open("../data/mainDB.pkl", "rb") as infile:
           chordDB = pickle.load(infile)  # Loaded every call!
   ```

4. **Hardcoded Paths** - Not portable:
   ```python
   # Current
   open("../data/ASCIItab.txt")

   # Should use
   os.path.join(os.path.dirname(__file__), '..', 'data', 'ASCIItab.txt')
   ```

---

*Generated: January 2026*
