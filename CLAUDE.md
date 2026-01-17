# CLAUDE.md - AI Assistant Guide for OCR-tabber

This document provides comprehensive guidance for AI assistants working on the OCR-tabber codebase.

## Project Overview

**OCR-tabber** is a Python application that scans images containing guitar tablature and converts them into ASCII text format. It uses Optical Character Recognition (OCR) via Tesseract to extract tab notation and includes chord recognition capabilities using a pre-existing chord database.

### Key Characteristics
- **Project Age**: ~11 years (last major commit December 2014)
- **Current State**: Legacy Python 2 codebase, proof-of-concept requiring modernization
- **Primary Language**: Python (currently Python 2, needs migration to Python 3)
- **Main Dependencies**: Python Tesseract (deprecated), pickle for data serialization
- **License**: Apache License 2.0
- **Chord Database**: GPL 2.0 (from Gnome Guitar project)

## Repository Structure

```
OCR-tabber/
├── src/                          # Source code directory
│   ├── ocr-tab.py               # Main OCR processing script
│   ├── chord-recognizer.py      # Chord recognition from ASCII tabs
│   ├── tabDBextractor.py        # XML to pickle database converter
│   └── tessdata/                # Tesseract training data and configs
│       ├── configs/             # Tesseract configuration files
│       ├── tessconfigs/         # Additional Tesseract settings
│       ├── eng.traineddata      # English language training data
│       └── *.cube.*             # Cube OCR engine data files
├── data/                         # Data files
│   ├── ASCIItab.txt             # Sample ASCII tab input
│   ├── mainDB.xml               # Original chord database (XML)
│   ├── mainDB.pkl               # Pickled chord database
│   └── testDB.xml               # Test database
├── README.md                     # Basic project documentation
├── DEVELOPMENT_PLAN.md           # Comprehensive audit and roadmap
├── LICENSE.md                    # Apache 2.0 license
└── .gitignore                   # Git ignore rules
```

## Core Components

### 1. ocr-tab.py (src/ocr-tab.py:1-33)
**Purpose**: Main entry point for OCR processing of guitar tab images.

**Functionality**:
- Initializes Tesseract API with English language model
- Sets character whitelist optimized for guitar tabs: `0123456789ABCDEFGabcdefghp-\/|`
- Processes image files via command line argument
- Outputs recognized ASCII tablature

**Current Issues**:
- Python 2 syntax (`print` statements without parentheses)
- Uses deprecated `tesseract` module instead of `pytesseract`
- No error handling for file I/O operations
- Hardcoded paths (assumes running from specific directory)
- No input validation on command line arguments

**Usage**: `python ocr-tab.py <image_file>`

### 2. chord-recognizer.py (src/chord-recognizer.py:1-84)
**Purpose**: Analyzes ASCII tablature to identify and recognize chords.

**Functionality**:
- Reads ASCII tab from `../data/ASCIItab.txt`
- Parses string tuning from first character of each line
- Extracts note positions (string number, fret number, position)
- Identifies chords by finding notes at the same horizontal position
- Matches identified chords against database
- Suggests alternate fingerings for recognized chords

**Current Issues**:
- **CRITICAL PERFORMANCE BUG**: Loads entire pickle database on every chord recognition call (src/chord-recognizer.py:41)
- Python 2 print syntax
- Hardcoded file paths
- No error handling
- Contains commented-out debug code

**Key Algorithm**:
1. Parse tab line-by-line, extracting notes and positions
2. Sort notes by horizontal position
3. Group notes at same position as potential chords
4. Query database for chord name
5. Display chord name and alternate fingerings

### 3. tabDBextractor.py (src/tabDBextractor.py:1-40)
**Purpose**: Utility to convert Gnome Guitar's XML chord database to pickle format.

**Functionality**:
- Parses `mainDB.xml` using ElementTree
- Extracts chord names and fret positions
- Creates list of [chord_name, fret_notation] pairs
- Serializes to `mainDB.pkl` using pickle

**Current Issues**:
- Python 2 syntax
- Unused import (`json`)
- Hardcoded paths
- No error handling
- Pickle format (security concern for untrusted data)

**Chord Format**: `"E None A 3 D 2 G 0 B 1 E 0"` (string tuning + fret number pairs)

## Technical Debt & Known Issues

Refer to `DEVELOPMENT_PLAN.md` for the comprehensive audit. Critical issues include:

### 🔴 Critical Priority
1. **Python 2 → 3 Migration** - Code will not run on Python 3
2. **No requirements.txt** - Cannot reproduce environment
3. **Deprecated Tesseract module** - Need `pytesseract` instead
4. **No error handling** - All file operations can crash
5. **Hardcoded paths** - Scripts only work from specific directories

### 🟠 High Priority
6. **Performance bug** - Database loaded per chord (should load once)
7. **No input validation** - No checks on CLI args or file types
8. **Zero test coverage** - No test suite exists
9. **Print debugging** - Need proper logging framework
10. **No package structure** - Missing setup.py/pyproject.toml

See `DEVELOPMENT_PLAN.md` for complete list of 21 issues and recommended fixes.

## Development Workflow

### Current Branch
- Working branch: `claude/add-claude-documentation-w5XDj`
- All development should occur on this branch
- Main branch: (not specified in context)

### Git Guidelines
1. Always develop on the designated `claude/*` branch
2. Use clear, descriptive commit messages
3. Push with: `git push -u origin <branch-name>`
4. Branch must start with `claude/` and match session ID
5. For network failures, retry up to 4 times with exponential backoff (2s, 4s, 8s, 16s)

### Making Changes
When working on this codebase:

1. **Read files before modifying** - Always examine existing code first
2. **Consider Python 2 compatibility** - Current code is Python 2; note any migration needs
3. **Be aware of path dependencies** - Many scripts use relative paths (`../data/`)
4. **Test manually** - No automated test suite exists yet
5. **Document issues** - Update DEVELOPMENT_PLAN.md if discovering new problems

## AI Assistant Guidelines

### Before Making Changes
1. ✅ **Always read files before proposing changes**
2. ✅ **Check for related code** - OCR, chord recognition, and database extraction are interconnected
3. ✅ **Consider path dependencies** - Scripts assume they're run from `src/` directory
4. ✅ **Review DEVELOPMENT_PLAN.md** - Understand existing technical debt
5. ✅ **Test impact on workflow** - Scripts are designed to run in sequence

### Coding Conventions
- **Python Version**: Currently Python 2 (target: Python 3.8+)
- **Import Style**: Standard library first, third-party second, local last
- **Error Handling**: Currently minimal; add try-except for all I/O operations
- **Path Handling**: Use `os.path.join()` and `__file__`-relative paths
- **Variable Naming**: Current code uses Hungarian notation (`mImgFile`) - acceptable but not required for new code

### Security Considerations
- **Pickle Usage**: Current code uses pickle for database serialization
  - Security risk if loading untrusted data
  - Consider migrating to JSON format
- **File I/O**: No validation of file paths or types
  - Add input validation for all user-supplied paths
- **Command Injection**: OCR input is relatively safe but validate image formats

### Performance Considerations
- **Critical**: chord-recognizer.py loads database on every call (src/chord-recognizer.py:40-41)
  - Load database ONCE at module level or in main()
  - This is a ~500KB file being deserialized repeatedly
- **Tesseract Initialization**: API initialized once per run (acceptable)
- **File I/O**: Files read entirely into memory (acceptable for typical tab images)

### Common Tasks

#### Running OCR on a Tab Image
```bash
cd src/
python ocr-tab.py ../path/to/tab-image.png
```

#### Recognizing Chords from ASCII Tab
```bash
cd src/
# Ensure ../data/ASCIItab.txt contains the tab
python chord-recognizer.py
```

#### Rebuilding Chord Database
```bash
cd src/
python tabDBextractor.py
# Reads ../data/mainDB.xml
# Writes ../data/mainDB.pkl
```

### Testing Strategy
Currently no test suite exists. When adding tests:

1. **Unit Tests**: Test individual functions
   - `chordRecognition()` with known chord patterns
   - Database loading/parsing
   - ASCII tab parsing logic

2. **Integration Tests**: Test full workflows
   - OCR → ASCII → Chord recognition pipeline
   - Database extraction from XML

3. **Test Data**: Use `testDB.xml` as starting point
   - Create sample tab images for OCR testing
   - Maintain ASCII tab fixtures for chord recognition

4. **Test Framework**: Recommend `pytest` for Python 3 migration

## Dependencies

### Current (Python 2)
- `tesseract` - Python Tesseract bindings (DEPRECATED)
- `xml.etree.ElementTree` - XML parsing (stdlib)
- `pickle` - Object serialization (stdlib)
- `operator` - Utility functions (stdlib)

### Recommended (Python 3 Migration)
Create `requirements.txt`:
```
pytesseract>=0.3.10
Pillow>=9.0.0
```

System requirements:
- Tesseract OCR engine (tesseract-ocr package)
- Tesseract English training data (tesseract-ocr-eng)

## File Reference Guide

### Critical Files for AI Context
When working on specific features, prioritize reading these files:

**OCR-related work**:
- `src/ocr-tab.py` - Main OCR logic
- `src/tessdata/` - Tesseract configuration

**Chord recognition work**:
- `src/chord-recognizer.py` - Chord matching logic
- `data/mainDB.pkl` or `data/mainDB.xml` - Chord database

**Database work**:
- `src/tabDBextractor.py` - Database conversion
- `data/mainDB.xml` - Source chord database

**Project planning**:
- `DEVELOPMENT_PLAN.md` - Complete audit and roadmap
- `README.md` - User-facing documentation

### Data Format Specifications

#### ASCII Tab Format (data/ASCIItab.txt)
```
E|--0--2--3--
B|--0--0--0--
G|--1--2--0--
D|--2--2--0--
A|--2--0--2--
E|--0-----3--
```
- First character: String tuning (must be in `[a-gA-G]`)
- Separator: `|` marks string line start
- Delimiters: `-` separates fret positions
- Numbers: Fret numbers (0-24 typically)

#### Chord Database Format
**XML** (mainDB.xml):
```xml
<chord name="C">
  <voiceing>
    <guitarString>
      <string>E</string>
      <visible>true</visible>
      <fret>0</fret>
    </guitarString>
    ...
  </voiceing>
</chord>
```

**Pickle** (mainDB.pkl):
```python
[
  ["C", "E 0 B 1 G 0 D 2 A 3 E None"],
  ["C", "E 3 B 5 G 5 D 5 A 3 E None"],
  ...
]
```
Format: `[chord_name, "string1 fret1 string2 fret2 ..."]`

## Modernization Roadmap

Refer to `DEVELOPMENT_PLAN.md` for the complete phased approach:

### Phase 1 - Make It Work (Critical)
Priority fixes to get code running on Python 3:
1. Python 3 migration (print statements, string handling)
2. Create requirements.txt
3. Replace tesseract → pytesseract
4. Add error handling to all file I/O
5. Fix hardcoded paths with os.path

### Phase 2 - Make It Testable (High Priority)
Essential improvements for maintainability:
6. Fix database loading performance bug
7. Add input validation
8. Create test suite with pytest
9. Replace print with logging module
10. Add pyproject.toml

### Phase 3 - Make It Usable (Features)
User-facing improvements:
11. CLI with argparse (replace raw sys.argv)
12. Batch processing mode
13. Multiple output formats (JSON, MusicXML, PDF)
14. Config file support (YAML/TOML)

### Phase 4 - Make It Professional (Polish)
Code quality improvements:
15. Add type hints throughout
16. Add comprehensive docstrings
17. Linting config (flake8, black, mypy)
18. CI/CD pipeline (GitHub Actions)
19. Dockerfile for reproducible environment
20. Expanded README with examples

### Phase 5 - Expand Capabilities (Future)
Advanced features:
- Web API (Flask/FastAPI)
- Image preprocessing pipeline
- Bass tab support
- MIDI export
- Machine learning-based OCR model

## Common Pitfalls

### ❌ Don't Do This
```python
# Running from wrong directory
cd OCR-tabber/
python src/ocr-tab.py image.png  # Will fail - can't find tessdata

# Modifying chord-recognizer.py without fixing the performance bug
# Every chord recognition loads the entire 500KB database

# Using Python 3 syntax in current codebase
print("This will fail")  # Current code expects Python 2

# Assuming paths are absolute
open("../data/mainDB.pkl")  # Breaks if not run from src/
```

### ✅ Do This
```python
# Run from correct directory
cd src/
python ocr-tab.py ../test/image.png

# Fix performance bug first when working on chord-recognizer.py
# Load database once at module level

# Maintain Python 2 compatibility until migration is complete
print "This works in Python 2"  # Or plan full Python 3 migration

# Use path-independent file access
import os
db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'mainDB.pkl')
```

## Questions to Ask

When uncertain about implementation decisions:

1. **Python Version**: "Should this change maintain Python 2 compatibility or assume Python 3 migration?"
2. **Scope**: "Does this change require updating other scripts (ocr-tab.py, chord-recognizer.py, tabDBextractor.py)?"
3. **Paths**: "Will this work regardless of the current working directory?"
4. **Dependencies**: "Does this require new external dependencies? Should I update requirements.txt?"
5. **Database Format**: "Does this change affect the chord database format or require re-running tabDBextractor.py?"
6. **Testing**: "How can this be tested without an automated test suite?"
7. **Backward Compatibility**: "Will this break existing usage patterns or data files?"

## Resources

### Documentation
- [Python Tesseract](https://github.com/madmaze/pytesseract) - Recommended library
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) - OCR engine
- [Gnome Guitar](http://gnome-chord.sourceforge.net/) - Chord database source

### Related Files
- `DEVELOPMENT_PLAN.md` - Comprehensive audit and prioritized roadmap
- `README.md` - User-facing project description
- `LICENSE.md` - Apache 2.0 license text

### Project Context
- Original author: Utkarsh Jaiswal (2014)
- Current maintainer: Unknown
- Last major update: December 2014
- Active development: Resumed January 2026 with AI assistance

## Working with Claude

### Effective Prompts
When requesting changes:

✅ **Good**: "Update chord-recognizer.py to load the database once at module level instead of on every function call"
- Specific file and issue
- Clear desired outcome
- Addresses known performance bug

✅ **Good**: "Migrate ocr-tab.py to Python 3, replacing the deprecated tesseract module with pytesseract"
- Clear scope (one file)
- Specific technical change
- Addresses known compatibility issue

❌ **Avoid**: "Make the code better"
- Too vague
- Unclear what "better" means
- No specific issue or outcome

❌ **Avoid**: "Fix all the bugs"
- Too broad
- Many unrelated changes
- See DEVELOPMENT_PLAN.md for prioritization

### Iterative Development
1. Start with DEVELOPMENT_PLAN.md priorities
2. Address critical issues before features
3. Test each change manually (no automated tests yet)
4. Update DEVELOPMENT_PLAN.md when issues are resolved
5. Document any new issues discovered

## Summary

OCR-tabber is a legacy Python 2 project requiring modernization. When working on this codebase:

1. **Understand the context** - 11-year-old proof-of-concept, not production code
2. **Read DEVELOPMENT_PLAN.md** - Contains comprehensive audit and roadmap
3. **Address technical debt** - Critical issues before new features
4. **Maintain workflow** - Scripts designed to run in sequence from src/ directory
5. **Test manually** - No automated testing infrastructure exists
6. **Document changes** - Update relevant documentation when making significant changes

The codebase is small (~120 lines total) but has significant technical debt. Prioritize fixes from DEVELOPMENT_PLAN.md Phase 1-2 before adding new features.

---

*Generated: January 17, 2026*
*For: AI Assistant Claude Code Sessions*
*Version: 1.0*
