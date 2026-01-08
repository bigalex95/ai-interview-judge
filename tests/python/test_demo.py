"""
Slide Detection Demo

This script demonstrates the usage of the AI Interview Judge's C++ slide detection module.
It processes a video file to detect slide transitions and saves preview images of detected slides.

Usage:
    python test_demo.py <path_to_video.mp4>

Example:
    python test_demo.py data/videos/presentation.mp4
"""

import sys
import os
import cv2
import time
from pathlib import Path
from typing import Optional, List

# Add project root and libs to Python path
PROJECT_ROOT = Path(__file__).parent.parent
LIBS_PATH = PROJECT_ROOT / "libs"
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(LIBS_PATH))

try:
    import ai_interview_cpp
except ImportError as e:
    print("❌ Failed to import C++ module!")
    print(f"Ensure .so/.pyd file is in the libs/ or backend/ directory")
    print(f"Details: {e}")
    sys.exit(1)


# Configuration constants
DEFAULT_MIN_SCENE_DURATION = 2.0
DEFAULT_MIN_AREA_RATIO = 0.15
DEFAULT_OUTPUT_DIR = "data/detected_slides"
TIMESTAMP_FONT = cv2.FONT_HERSHEY_SIMPLEX
TIMESTAMP_SCALE = 1.5
TIMESTAMP_COLOR = (0, 0, 255)  # Red in BGR
TIMESTAMP_THICKNESS = 3
TIMESTAMP_POSITION = (50, 50)


def validate_video(video_path: str) -> bool:
    """
    Validate that video file exists and is accessible.

    Args:
        video_path: Path to the video file

    Returns:
        True if video exists and is readable, False otherwise
    """
    if not os.path.exists(video_path):
        print(f"❌ Video file not found: {video_path}")
        return False

    if not os.path.isfile(video_path):
        print(f"❌ Path is not a file: {video_path}")
        return False

    return True


def process_video(detector, video_path: str) -> Optional[List]:
    """
    Process video with slide detection.

    Args:
        detector: SlideDetector instance
        video_path: Path to the video file

    Returns:
        List of detected slide segments, or None if processing failed
    """
    print(f"🚀 Processing video: {video_path}")

    start_time = time.time()
    try:
        segments = detector.process_video(video_path)
    except RuntimeError as e:
        print(f"❌ C++ Runtime Error: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return None

    elapsed = time.time() - start_time
    print(f"✅ Processing completed in {elapsed:.2f}s")
    print(f"📊 Detected {len(segments)} unique slide(s)")

    return segments


def save_detected_slides(
    detector, video_path: str, segments: List, output_dir: str = DEFAULT_OUTPUT_DIR
) -> None:
    """
    Save preview images of detected slides.

    Args:
        detector: SlideDetector instance
        video_path: Path to the video file
        segments: List of detected slide segments
        output_dir: Directory to save slide previews
    """
    os.makedirs(output_dir, exist_ok=True)
    print(f"\n💾 Saving slide previews to {output_dir}/...")

    for i, seg in enumerate(segments):
        frame = detector.get_frame(video_path, seg.frame_index)

        if frame is not None and frame.size > 0:
            # Draw timestamp on frame
            timestamp = f"{seg.timestamp_sec:.1f}s"
            cv2.putText(
                frame,
                timestamp,
                TIMESTAMP_POSITION,
                TIMESTAMP_FONT,
                TIMESTAMP_SCALE,
                TIMESTAMP_COLOR,
                TIMESTAMP_THICKNESS,
            )

            filename = f"{output_dir}/slide_{i:03d}_{int(seg.timestamp_sec)}s.jpg"
            cv2.imwrite(filename, frame)
            print(f"  ✓ {filename} (Change: {seg.change_ratio:.3f})")
        else:
            print(f"  ⚠ Failed to extract frame at index {seg.frame_index}")


def main():
    """
    Main entry point for slide detection demo.

    Parses command line arguments, initializes detector, processes video,
    and saves detected slide previews.
    """
    if len(sys.argv) < 2:
        print("❌ Error: Missing video file argument")
        print("\nUsage: python test_demo.py <path_to_video.mp4>")
        print("Example: python test_demo.py data/videos/presentation.mp4")
        sys.exit(1)

    video_path = sys.argv[1]

    if not validate_video(video_path):
        sys.exit(1)

    # Initialize detector with configured parameters
    print(f"\n⚙️  Initializing detector...")
    print(f"   - Min scene duration: {DEFAULT_MIN_SCENE_DURATION}s")
    print(f"   - Min area ratio: {DEFAULT_MIN_AREA_RATIO}")
    detector = ai_interview_cpp.SlideDetector(
        DEFAULT_MIN_SCENE_DURATION, DEFAULT_MIN_AREA_RATIO
    )

    # Process video
    segments = process_video(detector, video_path)
    if segments is None:
        sys.exit(1)

    if len(segments) == 0:
        print("\n⚠️  No slides detected in video")
        sys.exit(0)

    # Save results
    save_detected_slides(detector, video_path, segments)
    print(f"\n🎉 Done! Check the {DEFAULT_OUTPUT_DIR}/ directory")


if __name__ == "__main__":
    main()
