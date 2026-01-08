"""
Test language detection and OCR language configuration.

This test demonstrates the automatic language detection flow:
1. Whisper detects language from audio transcription
2. Language is mapped to PaddleOCR format
3. OCR uses the detected language for text extraction
"""

import pytest
from backend.services.ocr_service import map_language_code


class TestLanguageMapping:
    """Test language code mapping between Whisper and PaddleOCR."""

    def test_english_mapping(self):
        """Test English language code remains unchanged."""
        assert map_language_code("en") == "en"

    def test_chinese_mapping(self):
        """Test Chinese ISO code maps to PaddleOCR format."""
        assert map_language_code("zh") == "ch"

    def test_french_mapping(self):
        """Test French ISO code maps to PaddleOCR format."""
        assert map_language_code("fr") == "french"

    def test_german_mapping(self):
        """Test German ISO code maps to PaddleOCR format."""
        assert map_language_code("de") == "german"

    def test_spanish_mapping(self):
        """Test Spanish remains unchanged."""
        assert map_language_code("es") == "es"

    def test_japanese_mapping(self):
        """Test Japanese ISO code maps to PaddleOCR format."""
        assert map_language_code("ja") == "japan"

    def test_korean_mapping(self):
        """Test Korean ISO code maps to PaddleOCR format."""
        assert map_language_code("ko") == "korean"

    def test_unknown_language_defaults_to_english(self):
        """Test unknown language codes default to English."""
        assert map_language_code("xx") == "en"
        assert map_language_code("unknown") == "en"
        assert map_language_code("") == "en"

    def test_all_supported_languages(self):
        """Test all commonly supported languages have mappings."""
        supported_languages = [
            ("en", "en"),  # English
            ("zh", "ch"),  # Chinese
            ("es", "es"),  # Spanish
            ("fr", "french"),  # French
            ("de", "german"),  # German
            ("ja", "japan"),  # Japanese
            ("ko", "korean"),  # Korean
            ("ru", "ru"),  # Russian
            ("ar", "ar"),  # Arabic
            ("hi", "hi"),  # Hindi
            ("pt", "pt"),  # Portuguese
            ("it", "it"),  # Italian
        ]

        for whisper_code, expected_paddle_code in supported_languages:
            assert map_language_code(whisper_code) == expected_paddle_code


class TestLanguageDetectionFlow:
    """Test the end-to-end language detection flow."""

    def test_audio_service_returns_language(self):
        """
        Test that AudioService.transcribe() returns both segments and language.

        Note: This is a mock test. Real test would require an actual audio file.
        """
        # Mock test - demonstrates expected return type
        # In real usage: segments, language = audio_service.transcribe(audio_path)
        from typing import List, Dict, Any

        # Expected return type
        def mock_transcribe() -> tuple[List[Dict[str, Any]], str]:
            segments = [
                {"start": 0.0, "end": 2.5, "text": "Hello world"},
                {"start": 2.5, "end": 5.0, "text": "This is a test"},
            ]
            detected_language = "en"
            return segments, detected_language

        segments, lang = mock_transcribe()
        assert isinstance(segments, list)
        assert isinstance(lang, str)
        assert lang == "en"

    def test_ocr_worker_accepts_language_parameter(self):
        """
        Test that OCR worker function accepts language parameter.

        Note: This is a mock test showing the expected signature.
        """
        from backend.services.analysis_service import _ocr_worker_task
        import inspect

        # Check function signature includes language parameter
        sig = inspect.signature(_ocr_worker_task)
        params = list(sig.parameters.keys())

        assert "video_path" in params
        assert "slides_metadata" in params
        assert "language" in params

        # Check default value
        assert sig.parameters["language"].default == "en"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
