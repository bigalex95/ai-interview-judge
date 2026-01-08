import logging
import multiprocessing
from pathlib import Path
from typing import Any, Dict, List

import cv2

from backend.services.audio_service import AudioService

# Note: OcrService is NOT imported here to avoid library conflicts (OpenMP/MKL) with Torch/Whisper
# from backend.services.ocr_service import OcrService

logger = logging.getLogger(__name__)


def run_ocr_isolated(
    video_path: str, interval_sec: float = 2.0
) -> List[Dict[str, Any]]:
    """
    Runs OCR in a separate process to avoid library conflicts (OpenMP/MKL) with Torch.
    This function must be top-level to be picklable.
    """
    # Lazy import inside the spawned process
    import logging

    # Re-import cv2 here to ensure it's loaded in the worker process
    import cv2
    from backend.services.ocr_service import OcrService

    # Re-configure logging in the new process
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("OCR_Worker")

    logger.info("Initializing OCR Service in isolated process...")
    try:
        ocr_service = OcrService(lang="ru")
    except Exception as e:
        logger.error(f"Failed to init OCR in worker: {e}")
        return []

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logger.error("Could not open video for OCR")
        return []

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = max(int(fps * interval_sec), 1)

    extracted_data: List[Dict[str, Any]] = []
    frame_count = 0

    logger.info(f"Processing video {video_path} for OCR...")

    try:
        while True:
            success, frame = cap.read()
            if not success:
                break

            # Process only every N-th frame
            if frame_count % frame_interval == 0:
                timestamp = frame_count / fps if fps else 0.0

                # Run OCR
                try:
                    text = ocr_service.extract_text(frame)

                    # Basic noise filter and deduplication
                    if len(text) > 5:
                        if not extracted_data or extracted_data[-1]["text"] != text:
                            extracted_data.append(
                                {"timestamp": round(timestamp, 2), "text": text}
                            )
                            logger.info(
                                "Found text at %.1fs: %s...", timestamp, text[:30]
                            )
                except Exception as e:
                    logger.error(f"Frame processing error at {timestamp:.1f}s: {e}")

            frame_count += 1
    finally:
        cap.release()

    logger.info(f"OCR Complete. Found {len(extracted_data)} slides.")
    return extracted_data


class AnalysisService:
    """Coordinator service that runs the full multimodal analysis pipeline."""

    def __init__(self):
        # Initialize models once per application start
        self.audio_service = AudioService(model_size="base")

    def analyze_content(self, video_path: str) -> Dict[str, Any]:
        """Run audio transcription then slide text extraction."""
        path = Path(video_path)
        if not path.exists():
            raise FileNotFoundError(f"Video not found: {video_path}")

        logger.info("Starting analysis for: %s", video_path)

        # --- Phase 1: Audio Analysis ---
        logger.info("Phase 1: Audio Processing...")
        audio_file = self.audio_service.extract_audio(video_path)
        transcript = self.audio_service.transcribe(audio_file)

        # --- Phase 2: Visual Analysis (Slides) ---
        logger.info("Phase 2: Video OCR Processing (Isolated)...")

        # Use spawn context for a fresh interpreter
        # This prevents the 'std::exception' caused by torch/paddle shared lib conflicts
        ctx = multiprocessing.get_context("spawn")
        with ctx.Pool(processes=1) as pool:
            slides_content = pool.apply(run_ocr_isolated, (video_path, 2.0))

        return {
            "meta": {"video_path": video_path, "status": "completed"},
            "transcription": transcript,
            "visual_text": slides_content,
        }
