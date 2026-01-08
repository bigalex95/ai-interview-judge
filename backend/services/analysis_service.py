import logging
import multiprocessing
import re
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Dict, List, Set

import cv2

from backend.services.audio_service import AudioService

# Note: OcrService is NOT imported here to avoid library conflicts (OpenMP/MKL) with Torch/Whisper
# from backend.services.ocr_service import OcrService

logger = logging.getLogger(__name__)


def is_similar(a: str, b: str, threshold: float = 0.85) -> bool:
    """
    Проверяет, похожи ли две строки (Fuzzy Matching).
    """
    return SequenceMatcher(None, a, b).ratio() > threshold


def clean_generic_noise(text: str) -> str:
    """
    Базовая очистка: убирает только явный мусор (одиночные символы, странные знаки),
    но НЕ удаляет слова, основываясь на их смысле.
    """
    # Оставляем только буквы, цифры и базовую пунктуацию
    # Если слово состоит из 1 буквы и это не 'я', 'a' (англ) или цифра - убираем
    words = text.split()
    cleaned_words = []

    for w in words:
        # Убираем лишние символы по краям
        w_clean = w.strip(".,!?:;\"'|-«»")

        if not w_clean:
            continue

        # Фильтр совсем короткого мусора (одиночные согласные, случайные символы OCR)
        if (
            len(w_clean) < 2
            and not w_clean.isdigit()
            and w_clean.lower() not in ["я", "a", "i", "y", "v"]
        ):
            continue

        cleaned_words.append(w)

    return " ".join(cleaned_words)


def run_ocr_isolated(
    video_path: str, interval_sec: float = 2.0
) -> List[Dict[str, Any]]:
    """
    Запускает OCR в отдельном процессе. Возвращает "сырые" данные,
    которые потом будут очищены статистически.
    """
    import logging
    import cv2
    from backend.services.ocr_service import OcrService

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("OCR_Worker")

    try:
        ocr_service = OcrService(lang="ru")
    except Exception as e:
        logger.error(f"Failed to init OCR in worker: {e}")
        return []

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return []

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = max(int(fps * interval_sec), 1)

    raw_slides: List[Dict[str, Any]] = []
    frame_count = 0

    try:
        while True:
            success, frame = cap.read()
            if not success:
                break

            if frame_count % frame_interval == 0:
                timestamp = frame_count / fps if fps else 0.0
                try:
                    raw_text = ocr_service.extract_text(frame)
                    # Делаем только базовую очистку мусора
                    text = clean_generic_noise(raw_text)

                    if len(text) > 3:  # Если что-то осмысленное осталось
                        raw_slides.append(
                            {"timestamp": round(timestamp, 2), "text": text}
                        )
                except Exception as e:
                    pass

            frame_count += 1
    finally:
        cap.release()

    return raw_slides


class AnalysisService:
    """
    Coordinator service that runs the full multimodal analysis pipeline.
    """

    def __init__(self):
        self.audio_service = AudioService(model_size="base")

    def _post_process_slides(
        self, slides: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Умная фильтрация:
        1. Находит повторяющиеся слова (водяные знаки) независимо от регистра.
        2. Удаляет их.
        3. Объединяет слайды.
        """
        if not slides:
            return []

        # 1. Статистический анализ (с нормализацией)
        all_words_norm = []
        for s in slides:
            # Приводим к нижнему регистру для честной статистики
            words = s["text"].lower().split()
            # Убираем знаки препинания из слов для чистоты
            clean_words = [w.strip(".,!?:;\"'|-«»") for w in words]
            all_words_norm.extend(clean_words)

        if not all_words_norm:
            return slides

        word_counts = Counter(all_words_norm)
        total_slides = len(slides)

        # Если слово (в нижнем регистре) встречается чаще чем на 30% слайдов - это мусор
        watermark_threshold = 0.30
        watermark_words_lower = {
            word
            for word, count in word_counts.items()
            if count > total_slides * watermark_threshold
        }

        if watermark_words_lower:
            logger.info(f"Detected dynamic watermarks: {watermark_words_lower}")

        # 2. Очистка и дедупликация
        final_slides = []

        for s in slides:
            original_words = s["text"].split()
            # Фильтруем, проверяя lower() версию слова
            clean_words = [
                w
                for w in original_words
                if w.lower().strip(".,!?:;\"'|-«»") not in watermark_words_lower
            ]
            clean_text_str = " ".join(clean_words)

            # Если после очистки осталось < 3 символов (или пусто) - это был пустой слайд с логотипом
            if len(clean_text_str) < 3:
                continue

            # Дедупликация
            if not final_slides or not is_similar(
                clean_text_str, final_slides[-1]["text"]
            ):
                final_slides.append(
                    {"timestamp": s["timestamp"], "text": clean_text_str}
                )
            else:
                pass

        return final_slides

    def analyze_content(self, video_path: str) -> Dict[str, Any]:
        path = Path(video_path)
        if not path.exists():
            raise FileNotFoundError(f"Video not found: {video_path}")

        logger.info("Starting analysis for: %s", video_path)

        # Phase 1: Audio
        logger.info("Phase 1: Audio Processing...")
        audio_file = self.audio_service.extract_audio(video_path)
        transcript = self.audio_service.transcribe(audio_file)

        # Phase 2: Video (Raw Extraction)
        logger.info("Phase 2: Video OCR Extraction...")
        ctx = multiprocessing.get_context("spawn")
        with ctx.Pool(processes=1) as pool:
            raw_slides = pool.apply(run_ocr_isolated, (video_path, 2.0))

        # Phase 3: Post-processing (Cleaning & Deduplication)
        logger.info(f"Phase 3: Post-processing {len(raw_slides)} raw frames...")
        clean_slides = self._post_process_slides(raw_slides)
        logger.info(f"Final unique slides: {len(clean_slides)}")

        return {
            "meta": {"video_path": video_path, "status": "completed"},
            "transcription": transcript,
            "visual_text": clean_slides,
        }
