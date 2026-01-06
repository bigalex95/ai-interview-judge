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


def validate_video(video_path: str) -> bool:
    """Validate that video file exists and is accessible."""
    if not os.path.exists(video_path):
        print(f"❌ Video file not found: {video_path}")
        return False
    return True


def process_video(detector, video_path: str) -> Optional[List]:
    """Process video with slide detection."""
    print(f"🚀 Processing video: {video_path}")

    start_time = time.time()
    try:
        segments = detector.process_video(video_path)
    except RuntimeError as e:
        print(f"❌ C++ Error: {e}")
        return None

    elapsed = time.time() - start_time
    print(f"✅ Processing completed in {elapsed:.2f}s")
    print(f"📊 Detected unique slides: {len(segments)}")

    return segments


def save_detected_slides(
    detector, video_path: str, segments: List, output_dir: str = "data/detected_slides"
) -> None:
    """Save preview images of detected slides."""
    os.makedirs(output_dir, exist_ok=True)
    print(f"\nSaving slide previews to {output_dir}/...")

    for i, seg in enumerate(segments):
        frame = detector.get_frame(video_path, seg.frame_index)

        if frame is not None and frame.size > 0:
            # Draw timestamp on frame
            timestamp = f"{seg.timestamp_sec:.1f}s"
            cv2.putText(
                frame,
                timestamp,
                (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.5,
                (0, 0, 255),
                3,
            )

            filename = f"{output_dir}/slide_{i:03d}_{int(seg.timestamp_sec)}s.jpg"
            cv2.imwrite(filename, frame)
            print(f"  [✓] {filename} (Change Ratio: {seg.change_ratio:.3f})")
        else:
            print(f"  [⚠] Failed to extract frame at index {seg.frame_index}")


def main():
    """Main entry point for slide detection demo."""
    if len(sys.argv) < 2:
        print("Usage: python test_demo.py <path_to_video.mp4>")
        return

    video_path = sys.argv[1]

    if not validate_video(video_path):
        return

    # Initialize detector (min_scene_duration=2.0s, min_area_ratio=0.15)
    detector = ai_interview_cpp.SlideDetector(2.0, 0.15)

    # Process video
    segments = process_video(detector, video_path)
    if segments is None:
        return

    # Save results
    save_detected_slides(detector, video_path, segments)
    print(f"\n🎉 Done! Check the detected_slides/ directory")


if __name__ == "__main__":
    main()
