# Automatic Language Detection & OCR Configuration

## Overview

The AI Interview Judge now automatically detects the interview language from audio transcription and configures OCR (Optical Character Recognition) to use the same language for extracting text from slides.

## How It Works

### 1. **Language Detection (Phase 1: Audio Processing)**

When processing a video, Faster Whisper automatically detects the spoken language during transcription:

```python
# In audio_service.py
segments, info = self.model.transcribe(audio_path, beam_size=5)
detected_language = info.language  # e.g., 'en', 'es', 'fr', 'de'
```

The detected language is an ISO 639-1 code (e.g., `en` for English, `es` for Spanish).

### 2. **Language Propagation (Phase 2-3: Analysis Pipeline)**

The detected language flows through the analysis pipeline:

```python
# In analysis_service.py
transcript, detected_language = self.audio_service.transcribe(audio_file)
# Pass to OCR worker
visual_data = pool.apply(_ocr_worker_task, (video_path, detected_slides, detected_language))
```

### 3. **Language Mapping (Phase 3: OCR Initialization)**

Before initializing PaddleOCR, the ISO 639-1 code is mapped to PaddleOCR's format:

```python
# In ocr_service.py
def map_language_code(whisper_lang: str) -> str:
    language_map = {
        'en': 'en',      # English
        'zh': 'ch',      # Chinese
        'fr': 'french',  # French
        'de': 'german',  # German
        'ja': 'japan',   # Japanese
        'ko': 'korean',  # Korean
        # ... more languages
    }
    return language_map.get(whisper_lang, 'en')  # Default to English
```

### 4. **Dynamic OCR Configuration**

PaddleOCR is initialized with the detected language in the isolated worker process:

```python
# In OCR worker (_ocr_worker_task)
from backend.services.ocr_service import OcrService
ocr_service = OcrService(lang=detected_language)  # Dynamic language
```

### 5. **API Response**

The detected language is included in the response metadata:

```json
{
  "meta": {
    "video_path": "/path/to/video.mp4",
    "status": "completed",
    "detected_language": "en"
  },
  "transcription": [...],
  "visual_context": [...]
}
```

## Supported Languages

The system supports 20+ languages including:

| Language   | Whisper Code | PaddleOCR Code |
| ---------- | ------------ | -------------- |
| English    | `en`         | `en`           |
| Chinese    | `zh`         | `ch`           |
| Spanish    | `es`         | `es`           |
| French     | `fr`         | `french`       |
| German     | `de`         | `german`       |
| Japanese   | `ja`         | `japan`        |
| Korean     | `ko`         | `korean`       |
| Russian    | `ru`         | `ru`           |
| Arabic     | `ar`         | `ar`           |
| Hindi      | `hi`         | `hi`           |
| Portuguese | `pt`         | `pt`           |
| Italian    | `it`         | `it`           |
| Dutch      | `nl`         | `dutch`        |
| Polish     | `pl`         | `pl`           |
| Turkish    | `tr`         | `tr`           |

See [ocr_service.py](../backend/services/ocr_service.py) `map_language_code()` for the complete list.

## Error Handling

### Fallback Mechanism

If the detected language is not supported or OCR initialization fails:

1. **Unknown Language**: Defaults to English (`en`)
2. **OCR Initialization Failure**: Falls back to English model
3. **No Audio**: Uses English as default

```python
# Automatic fallback in OcrService.__init__()
try:
    self.ocr = PaddleOCR(use_angle_cls=False, lang=paddle_lang, show_log=False)
except Exception as e:
    logger.warning("Falling back to English (en)...")
    self.ocr = PaddleOCR(use_angle_cls=False, lang="en", show_log=False)
```

## Architecture Benefits

### Zero New Dependencies

- Uses **Whisper's built-in** language detection (already part of transcription)
- No additional language detection libraries needed
- Lightweight and efficient

### Seamless Integration

- No changes to API contract (backward compatible)
- Minimal code changes to existing services
- Maintains multiprocessing isolation for library conflict prevention

### Single Source of Truth

- One language detection point (audio transcription)
- Consistent language across audio and visual analysis
- Reduces complexity and potential mismatches

## Testing

Run the language detection tests:

```bash
python -m pytest tests/python/test_language_detection.py -v
```

Tests verify:

- ✅ Language code mapping (Whisper → PaddleOCR)
- ✅ Unknown language fallback to English
- ✅ Audio service returns language tuple
- ✅ OCR worker accepts language parameter

## Future Enhancements

### 1. Language Override API Parameter (Optional)

Allow users to force a specific language:

```python
@app.post("/analyze")
async def analyze_video_endpoint(
    file: UploadFile = File(...),
    force_language: Optional[str] = None  # Override auto-detection
):
    # Pass force_language to analysis_service
    result = analysis_service.analyze_content(
        str(file_path),
        force_language=force_language
    )
```

### 2. OCR-Only Language Detection (For Images Without Audio)

Add text-based language detection using `langdetect`:

```python
from langdetect import detect

def detect_text_language(text: str) -> str:
    try:
        return detect(text)
    except:
        return "en"
```

### 3. Language Confidence Metadata

Include Whisper's language detection confidence in the response:

```json
{
  "meta": {
    "detected_language": "en",
    "language_confidence": 0.95,
    "language_detection_method": "whisper_audio"
  }
}
```

### 4. Configuration Settings

Add configuration options to `config.py`:

```python
class Settings:
    # Language Detection
    DEFAULT_OCR_LANGUAGE: str = "en"
    ENABLE_LANGUAGE_DETECTION: bool = True
    FALLBACK_TO_ENGLISH: bool = True
```

## Implementation Summary

**Files Modified:**

- [audio_service.py](../backend/services/audio_service.py) — Returns `(segments, language)` tuple
- [analysis_service.py](../backend/services/analysis_service.py) — Propagates language to OCR worker
- [ocr_service.py](../backend/services/ocr_service.py) — Maps language codes & dynamic OCR init

**Files Created:**

- [test_language_detection.py](../tests/python/test_language_detection.py) — Test suite for language detection

**Lines Changed:** ~80 LOC
**New Dependencies:** 0
**Breaking Changes:** None (backward compatible)

## Example Usage

### Processing a Spanish Interview

```python
# Video contains Spanish audio
result = analysis_service.analyze_content("spanish_interview.mp4")

# Output:
{
  "meta": {
    "detected_language": "es",  # Auto-detected
    "status": "completed"
  },
  "transcription": [
    {"start": 0.0, "end": 3.5, "text": "Hola, mi nombre es Juan"}
  ],
  "visual_context": [
    {"timestamp": 5.0, "ocr_text": "Presentación Técnica"}  # OCR in Spanish
  ]
}
```

### Processing a French Interview

```python
result = analysis_service.analyze_content("french_interview.mp4")

# Output:
{
  "meta": {
    "detected_language": "fr",  # Mapped to "french" for PaddleOCR
    "status": "completed"
  },
  "transcription": [
    {"start": 0.0, "end": 4.0, "text": "Bonjour, je m'appelle Marie"}
  ],
  "visual_context": [
    {"timestamp": 8.0, "ocr_text": "Présentation Technique"}  # OCR in French
  ]
}
```

## Conclusion

The automatic language detection feature provides:

- ✅ **Zero configuration** — Works out of the box
- ✅ **20+ languages** — Supports major world languages
- ✅ **Robust fallback** — Defaults to English on errors
- ✅ **Efficient** — Leverages existing Whisper detection
- ✅ **Maintainable** — Simple, clean implementation

No user intervention required — the system automatically adapts to the interview language!
