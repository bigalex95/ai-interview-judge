import logging
import os
import shutil
from pathlib import Path
from typing import List, Dict, Any
from faster_whisper import WhisperModel
from moviepy.editor import VideoFileClip

logger = logging.getLogger(__name__)


class AudioService:
    """
    Service for audio extraction and transcription using Faster Whisper.
    """

    def __init__(self, model_size: str = "base"):
        logger.info(f"Loading Faster Whisper model ('{model_size}')...")
        try:
            # model is loaded to RAM - faster-whisper is more efficient
            # device: "cpu" or "cuda", compute_type: "int8" for CPU efficiency
            self.model = WhisperModel(model_size, device="cpu", compute_type="int8")
            logger.info("Faster Whisper model loaded.")
        except Exception as e:
            logger.error(f"Failed to load Faster Whisper: {e}")
            raise RuntimeError("Whisper initialization failed") from e

    def extract_audio(self, video_path: str, output_dir: str = "temp_audio") -> str:
        """Extracts audio track from video to MP3."""
        Path(output_dir).mkdir(exist_ok=True)
        video_filename = Path(video_path).stem
        audio_path = f"{output_dir}/{video_filename}.mp3"

        if os.path.exists(audio_path):
            logger.info(f"Audio already extracted: {audio_path}")
            return audio_path

        try:
            logger.info(f"Extracting audio from {video_path}...")
            video = VideoFileClip(video_path)
            # Извлекаем аудио (bitrate 128k достаточно для речи)
            video.audio.write_audiofile(
                audio_path, bitrate="128k", verbose=False, logger=None
            )
            video.close()
            return audio_path
        except Exception as e:
            logger.error(f"Audio extraction failed: {e}")
            raise RuntimeError("FFmpeg extraction failed") from e

    def transcribe(self, audio_path: str) -> List[Dict[str, Any]]:
        """
        Transcribes audio file.
        Returns list of segments: {'start': 0.0, 'end': 4.0, 'text': 'Hello world'}
        """
        try:
            logger.info(f"Starting transcription for {audio_path}...")
            # faster-whisper returns generator of segments
            segments, info = self.model.transcribe(audio_path, beam_size=5)

            # Convert generator to list of dicts matching original format
            result_segments = []
            for segment in segments:
                result_segments.append(
                    {"start": segment.start, "end": segment.end, "text": segment.text}
                )

            return result_segments
        except Exception as e:
            logger.error(f"Whisper transcription failed: {e}")
            raise RuntimeError("Transcription failed") from e
        finally:
            # Очистка (опционально, если хотим удалять аудио сразу)
            pass
