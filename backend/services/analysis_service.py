import logging
import multiprocessing
import cv2
from pathlib import Path
from typing import Any, Dict, List

from backend.services.audio_service import AudioService
from backend.services.video_service import SlideDetectionService
from backend.services.llm_service import LLMJudgeService

# ВАЖНО: НЕ импортируем OcrService здесь на верхнем уровне,
# чтобы не спровоцировать загрузку Paddle в основном процессе.

logger = logging.getLogger(__name__)


def _ocr_worker_task(
    video_path: str, slides_metadata: List[Dict], language: str = "en"
) -> List[Dict]:
    """
    Эта функция запускается в ОТДЕЛЬНОМ процессе.
    Здесь безопасно грузить PaddleOCR, так как Torch здесь нет.

    Args:
        video_path: Path to the video file
        slides_metadata: List of detected slides with frame_index and timestamp
        language: ISO 639-1 language code detected from audio (e.g., 'en', 'es', 'fr')
    """
    import logging

    # Настраиваем логи для дочернего процесса
    logging.basicConfig(level=logging.INFO)
    worker_logger = logging.getLogger("OCR_Worker")

    worker_logger.info(
        f"Worker started. Processing {len(slides_metadata)} slides with language={language}..."
    )

    results = []
    cap = None

    try:
        # --- FIX: Запрещаем Paddle перехватывать системные сигналы (SIGTERM) ---
        import paddle

        paddle.disable_signal_handler()
        # -----------------------------------------------------------------------

        # 1. Lazy Import внутри процесса
        from backend.services.ocr_service import OcrService

        ocr_service = OcrService(lang=language)

        # 2. Открываем видео (OpenCV безопасен в мультипроцессинге)
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            worker_logger.error("Failed to open video in worker")
            return []

        # 3. Пробегаем по списку найденных слайдов
        for slide in slides_metadata:
            frame_idx = slide["frame_index"]
            timestamp = slide["timestamp_sec"]

            # Прыгаем к кадру
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()

            if ret:
                text = ocr_service.extract_text(frame)
                if text and len(text.strip()) > 3:
                    results.append(
                        {
                            "timestamp": timestamp,
                            "frame_index": frame_idx,
                            "ocr_text": text,
                        }
                    )
    except Exception as e:
        worker_logger.error(f"Worker crashed: {e}")
    finally:
        if cap:
            cap.release()

    worker_logger.info(f"Worker finished. Found text on {len(results)} slides.")
    return results


class AnalysisService:
    """
    Coordinator service that runs the full multimodal analysis pipeline.
    """

    def __init__(self):
        # В основном процессе живет только Whisper (Torch) и C++ детектор
        self.audio_service = AudioService(model_size="base")
        self.video_service = SlideDetectionService(
            min_scene_duration=2.0, min_area_ratio=0.15
        )
        self.llm_service = LLMJudgeService()

    def analyze_content(self, video_path: str) -> Dict[str, Any]:
        path = Path(video_path)
        if not path.exists():
            raise FileNotFoundError(f"Video not found: {video_path}")

        logger.info("🚀 Starting analysis for: %s", video_path)

        # --- Phase 1: Audio Processing (Main Process) ---
        # Whisper работает здесь
        logger.info("🎧 Phase 1: Audio Processing...")
        transcript = []
        detected_language = "en"  # Default fallback
        try:
            audio_file = self.audio_service.extract_audio(video_path)
            transcript, detected_language = self.audio_service.transcribe(audio_file)
            logger.info(
                f"✅ Transcribed {len(transcript)} segments in {detected_language}"
            )
        except Exception as e:
            logger.error(f"Audio processing failed: {e}")

        # --- Phase 2: Visual Processing (C++ Detection) ---
        # C++ работает здесь (быстро и без конфликтов)
        logger.info("👁️ Phase 2: Visual Processing (Detection)...")
        detected_slides = []
        try:
            detected_slides = self.video_service.process_video(video_path)
            logger.info(f"⚡ C++ detected {len(detected_slides)} keyframes")
        except Exception as e:
            logger.error(f"Slide detection failed: {e}")

        # --- Phase 3: OCR (Isolated Process) ---
        # Запускаем Paddle в отдельной "песочнице"
        logger.info(
            f"📖 Phase 3: OCR Extraction (Isolated, lang={detected_language})..."
        )
        visual_data = []
        if detected_slides:
            # Используем 'spawn', чтобы процесс был чистым (без Torch в памяти)
            ctx = multiprocessing.get_context("spawn")
            with ctx.Pool(processes=1) as pool:
                # Передаем путь к видео, список кадров, и detected language
                visual_data = pool.apply(
                    _ocr_worker_task, (video_path, detected_slides, detected_language)
                )

        # Собираем сырые данные
        analysis_result = {
            "meta": {
                "video_path": str(video_path),
                "status": "completed",
                "detected_language": detected_language,
            },
            "transcription": transcript,
            "visual_context": visual_data,
        }

        # --- [NEW] Phase 4: LLM Evaluation ---
        logger.info("🧠 Phase 4: LLM Evaluation...")
        # Передаем собранные данные (текст + слайды) в Gemini
        ai_feedback = self.llm_service.evaluate_interview(analysis_result)

        # Добавляем оценку в финальный ответ
        analysis_result["ai_evaluation"] = ai_feedback

        return analysis_result
