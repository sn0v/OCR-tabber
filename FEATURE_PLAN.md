# OCR-tabber Feature Plan

This document outlines planned features for OCR-tabber, prioritized by value and implementation order.

---

## MVP+ (Build First)

These features form the core product that's actually useful end-to-end.

1. **Validate OCR accuracy** - Test current Tesseract approach with real tab images
2. **Image preprocessing pipeline** - Deskew, contrast adjustment, noise removal
3. **Confidence scoring** - Return confidence levels for recognition results
4. **Simple correction UI** - Let users fix OCR errors quickly
5. **Chord diagram generation** - Visual fingering charts alongside text output

---

## High Priority (Core Value)

| Feature | Description | Why |
|---------|-------------|-----|
| Image preprocessing | Deskew, contrast, denoise before OCR | Directly improves accuracy |
| Confidence scoring | Return confidence % for each recognized element | Users need to know what might be wrong |
| Manual correction UI | Edit/fix OCR mistakes in the GUI | OCR will never be 100% accurate |
| Multiple output formats | Plain text, JSON, MusicXML export | Different users need different formats |
| Chord diagram generation | Visual fingering charts (SVG/PNG) | Huge UX improvement over text-only |
| Batch processing | Process a folder of images at once | Common workflow for scanning songbooks |

---

## Medium Priority (Expand Use Cases)

| Feature | Description | Why |
|---------|-------------|-----|
| PDF/multi-page support | Parse entire songbook PDFs | Scanned songbooks are common |
| Bass tab support | Handle 4-string bass tablature | Expands audience |
| Alternative tunings | Drop D, Open G, DADGAD, etc. | Required for many songs |
| MIDI export | Convert recognized tabs to MIDI | Hear what you scanned |
| Camera capture | Point phone/webcam at tab, scan directly | Mobile/desktop convenience |
| Tab library/organizer | Save, tag, search your collection | Long-term usability |
| Audio playback preview | Play back the tab as audio | Hear without external software |

---

## Low Priority (Power User / Future)

| Feature | Description | Why |
|---------|-------------|-----|
| Guitar Pro format export | Export to .gp5/.gpx format | Niche but dedicated users want it |
| Tempo/metronome integration | Set BPM, practice with click track | Practice tool, scope creep territory |
| Loop sections for practice | Repeat specific measures | Entering "practice app" territory |
| YouTube video sync | Display tab alongside video playback | Cool but complex |
| Ultimate Guitar integration | Fetch/compare against UG database | API access and legal complexity |
| Custom ML OCR model | Train model specifically for guitar tabs | High effort, pursue if Tesseract fails |
| Impossible fingering detection | Warn when chord is physically unplayable | Nice polish, not essential |

---

## Technical Decisions (Pending)

### Language/Framework
- **Current**: Python + pytesseract
- **Considering**: Rust + Tauri, Go + Wails, or Kotlin + Compose Multiplatform
- **Decision**: Validate OCR approach first in Python, then decide on rewrite

### OCR Strategy
- **Current**: Tesseract with character whitelist
- **Alternatives to evaluate**:
  - EasyOCR (deep learning based)
  - PaddleOCR (excellent accuracy)
  - Custom CV approach (detect 6 lines, segment columns, template match)
  - Cloud APIs (Google Vision, AWS Textract)
- **Decision**: Test accuracy with real images before committing

### GUI Toolkit
- **Candidates**: Tauri, Wails, Fyne, Compose Multiplatform, Electron
- **Decision**: Depends on language choice above

---

## Success Metrics

- OCR accuracy rate on standard tab images (target: >90%)
- Chord recognition accuracy (target: >95% for chords in database)
- Time to process single image (target: <2 seconds)
- User correction rate (lower is better)

---

*Created: January 2026*
