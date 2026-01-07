"""
Video Processing Service

Handles video processing, slide detection, and frame extraction.
"""

import sys
from pathlib import Path
from typing import List, Optional, Dict, Any
import logging

# Setup path for C++ module
PROJECT_ROOT = Path(__file__).parent.parent.parent
LIBS_PATH = PROJECT_ROOT / "libs"
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(LIBS_PATH))

logger = logging.getLogger(__name__)


class VideoProcessingError(Exception):
    """Raised when video processing fails."""

    pass


class SlideDetectionService:
    """
    Service for detecting slide transitions in videos.

    This service wraps the C++ slide detection module and provides
    a clean Python interface for video processing.
    """

    def __init__(self, min_scene_duration: float = 2.0, min_area_ratio: float = 0.15):
        """
        Initialize the slide detection service.

        Args:
            min_scene_duration: Minimum duration between slides (seconds)
            min_area_ratio: Minimum area ratio for slide detection (0.0-1.0)

        Raises:
            ImportError: If C++ module cannot be loaded
        """
        self.min_scene_duration = min_scene_duration
        self.min_area_ratio = min_area_ratio

        try:
            import ai_interview_cpp

            self._cpp_module = ai_interview_cpp
            self._detector = ai_interview_cpp.SlideDetector(
                min_scene_duration, min_area_ratio
            )
            logger.info("Slide detector initialized successfully")
        except ImportError as e:
            logger.error(f"Failed to import C++ module: {e}")
            raise ImportError(
                "C++ module not found. Please build the project first using scripts/build.sh"
            ) from e

    def process_video(self, video_path: str) -> List[Dict[str, Any]]:
        """
        Process a video file to detect slide transitions.

        Args:
            video_path: Path to the video file

        Returns:
            List of dictionaries containing slide information:
            - frame_index: Frame number where slide appears
            - timestamp_sec: Timestamp in seconds
            - change_ratio: Change ratio compared to previous slide

        Raises:
            VideoProcessingError: If video processing fails
            FileNotFoundError: If video file doesn't exist
        """
        video_path_obj = Path(video_path)
        if not video_path_obj.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")

        if not video_path_obj.is_file():
            raise ValueError(f"Path is not a file: {video_path}")

        try:
            logger.info(f"Processing video: {video_path}")
            segments = self._detector.process_video(str(video_path))

            # Convert C++ objects to dictionaries
            result = [
                {
                    "frame_index": seg.frame_index,
                    "timestamp_sec": seg.timestamp_sec,
                    "change_ratio": seg.change_ratio,
                }
                for seg in segments
            ]

            logger.info(f"Detected {len(result)} slides in video")
            return result

        except RuntimeError as e:
            logger.error(f"C++ processing error: {e}")
            raise VideoProcessingError(f"Failed to process video: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error during video processing: {e}")
            raise VideoProcessingError(f"Unexpected error: {e}") from e

    def get_frame(self, video_path: str, frame_index: int):
        """
        Extract a specific frame from a video.

        Args:
            video_path: Path to the video file
            frame_index: Index of the frame to extract

        Returns:
            Numpy array representing the frame (BGR format)

        Raises:
            VideoProcessingError: If frame extraction fails
        """
        try:
            frame = self._detector.get_frame(video_path, frame_index)
            if frame is None or frame.size == 0:
                raise VideoProcessingError(f"Failed to extract frame {frame_index}")
            return frame
        except Exception as e:
            logger.error(f"Failed to extract frame: {e}")
            raise VideoProcessingError(f"Frame extraction failed: {e}") from e

    def get_configuration(self) -> Dict[str, Any]:
        """
        Get current detector configuration.

        Returns:
            Dictionary with configuration parameters
        """
        return {
            "min_scene_duration": self.min_scene_duration,
            "min_area_ratio": self.min_area_ratio,
        }
