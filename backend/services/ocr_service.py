import logging
import os

# Fix for OpenMP conflict (common in PyTorch/Paddle + FastAPI)
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# --- FIX: Отключаем MKLDNN для предотвращения конфликта OneDNN ---
os.environ["FLAGS_use_mkldnn"] = "0"
os.environ["FLAGS_enable_mkldnn"] = "0"
# -----------------------------------------------------------------

import cv2
import numpy as np
from paddleocr import PaddleOCR

logger = logging.getLogger(__name__)


class OcrService:
    """
    Service for extracting text from images using PaddleOCR.
    """

    def __init__(self, lang: str = "ru"):
        """Initialize PaddleOCR model.

        Args:
            lang: Language code ('en', 'ru', 'ch', etc.)
        """
        logger.info(f"Loading PaddleOCR model (lang={lang})...")
        try:
            # Инициализация модели (Heavy operation!)
            # use_angle_cls=True позволяет читать перевернутый текст
            # Note: use_angle_cls is deprecated, using use_textline_orientation=True if possible,
            # but keeping compat. PaddleOCR constructor handles kwarg mapping usually.
            self.ocr = PaddleOCR(
                use_angle_cls=False,
                lang=lang,
            )
            logger.info("PaddleOCR model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load PaddleOCR: {e}")
            raise RuntimeError("OCR Model initialization failed") from e

    def extract_text(self, frame: np.ndarray) -> str:
        """
        Extract text from a single video frame.

        Returns:
            Combined string of all detected text lines.
        """
        if frame is None or frame.size == 0:
            return ""

        try:
            # Convert BGR (OpenCV) to RGB (PaddleOCR expects RGB)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Ensure uint8 type
            frame_rgb = frame_rgb.astype(np.uint8)

            if not frame_rgb.flags["C_CONTIGUOUS"]:
                frame_rgb = np.ascontiguousarray(frame_rgb)

            # Debug logs for troubleshooting
            # logger.info(f"Frame processing: shape={frame_rgb.shape}, dtype={frame_rgb.dtype}, contiguous={frame_rgb.flags['C_CONTIGUOUS']}")

            # result structure: [ [ [points], (text, confidence) ], ... ]
            result = self.ocr.ocr(frame_rgb, cls=False)

            if not result or result[0] is None:
                return ""

            # Собираем весь текст в одну строку
            extracted_lines = []

            # Handle new PaddleOCR output format (dict)
            if isinstance(result[0], dict):
                data = result[0]
                texts = data.get("rec_texts", [])
                scores = data.get("rec_scores", [])
                for text, score in zip(texts, scores):
                    if score > 0.6:
                        extracted_lines.append(text)
            # Handle standard PaddleOCR output format (list of lists)
            elif isinstance(result[0], list):
                for line in result[0]:
                    if isinstance(line, list) and len(line) >= 2:
                        text = line[1][0]
                        confidence = line[1][1]

                        # Фильтруем мусор с низкой уверенностью
                        if confidence > 0.6:
                            extracted_lines.append(text)

            full_text = " ".join(extracted_lines)
            return full_text

        except Exception as e:
            logger.error(f"OCR Inference error: {type(e).__name__}: {e}")
            return ""
