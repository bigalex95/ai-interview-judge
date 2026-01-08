import logging
import cv2
import numpy as np
import os

# Удаляем глобальный импорт paddleocr, чтобы не грузить либы раньше времени
# from paddleocr import PaddleOCR

logger = logging.getLogger(__name__)


def map_language_code(whisper_lang: str) -> str:
    """
    Map Whisper/ISO 639-1 language codes to PaddleOCR language format.

    Args:
        whisper_lang: ISO 639-1 language code from Whisper (e.g., 'en', 'es', 'fr')

    Returns:
        PaddleOCR language code (e.g., 'en', 'es', 'french', 'german')

    Note: PaddleOCR uses inconsistent naming - some are ISO codes, others are full names.
    See: https://github.com/PaddlePaddle/PaddleOCR/blob/release/2.7/doc/doc_en/multi_languages_en.md
    """
    # Mapping from Whisper ISO 639-1 codes to PaddleOCR language names
    language_map = {
        "en": "en",  # English
        "zh": "ch",  # Chinese (Simplified)
        "es": "es",  # Spanish
        "fr": "french",  # French
        "de": "german",  # German
        "ja": "japan",  # Japanese
        "ko": "korean",  # Korean
        "ru": "ru",  # Russian
        "ar": "ar",  # Arabic
        "hi": "hi",  # Hindi
        "pt": "pt",  # Portuguese
        "it": "it",  # Italian
        "nl": "dutch",  # Dutch
        "pl": "pl",  # Polish
        "tr": "tr",  # Turkish
        "vi": "vi",  # Vietnamese
        "th": "th",  # Thai
        "sv": "sv",  # Swedish
        "da": "da",  # Danish
        "no": "no",  # Norwegian
        "fi": "fi",  # Finnish
    }

    paddle_lang = language_map.get(whisper_lang, "en")
    if paddle_lang != whisper_lang:
        logger.info(f"Mapped language: {whisper_lang} -> {paddle_lang}")
    return paddle_lang


class OcrService:
    """
    Service for extracting text from images using PaddleOCR.
    """

    def __init__(self, lang: str = "en"):
        """Initialize PaddleOCR model.

        Args:
            lang: Language code (ISO 639-1 from Whisper or PaddleOCR format)
        """
        # Map language code to PaddleOCR format
        paddle_lang = map_language_code(lang)

        logger.info(f"Loading PaddleOCR model (lang={paddle_lang})...")
        try:
            # --- LAZY IMPORT (CRITICAL FIX) ---
            # Импортируем только здесь, чтобы этот код исполнялся ТОЛЬКО в воркере
            from paddleocr import PaddleOCR

            # use_angle_cls=False ускоряет и уменьшает шанс ошибок
            self.ocr = PaddleOCR(
                use_angle_cls=False,
                lang=paddle_lang,
                show_log=False,  # Убираем шум в консоли
            )
            logger.info(
                f"PaddleOCR model loaded successfully with language={paddle_lang}."
            )
        except Exception as e:
            logger.error(f"Failed to load PaddleOCR with lang={paddle_lang}: {e}")
            logger.warning("Falling back to English (en)...")
            # Fallback to English if the specified language fails
            try:
                from paddleocr import PaddleOCR

                self.ocr = PaddleOCR(use_angle_cls=False, lang="en", show_log=False)
                logger.info("PaddleOCR loaded with fallback language: en")
            except Exception as fallback_error:
                logger.error(f"Fallback to English also failed: {fallback_error}")
                raise RuntimeError("OCR Model initialization failed") from e

    def extract_text(self, frame: np.ndarray) -> str:
        """Extract text from a single video frame."""
        if frame is None or frame.size == 0:
            return ""

        try:
            # Paddle ожидает RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Инференс
            result = self.ocr.ocr(frame_rgb, cls=False)

            if not result or result[0] is None:
                return ""

            # Сборка текста
            extracted_lines = []

            # Обработка разных форматов ответа Paddle
            lines = result[0]
            if isinstance(lines, list):
                for line in lines:
                    # line format: [[points], [text, score]]
                    if len(line) >= 2 and isinstance(line[1], (list, tuple)):
                        text, score = line[1]
                        if score > 0.6:
                            extracted_lines.append(text)

            return " ".join(extracted_lines)

        except Exception as e:
            logger.error(f"OCR Inference error: {e}")
            return ""
