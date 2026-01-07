"""
AI Interview Judge - Main Entry Point

A multimodal AI system for automatically evaluating technical interviews and presentations.

This is the main entry point for the application. For development and testing,
use the backend/test_demo.py script to test the slide detection functionality.

Author: bigalex95
License: See LICENSE file
"""


def main():
    """
    Main entry point for the AI Interview Judge application.

    This function serves as the primary interface for the application.
    Currently, it provides basic information. For slide detection demo,
    use backend/test_demo.py instead.
    """
    print("=" * 60)
    print("AI Interview Judge \ud83e\udde0\u2696\ufe0f")
    print("=" * 60)
    print("\nA multimodal AI system for evaluating technical interviews.")
    print("\n\ud83d\ude80 Quick Start:")
    print("  - For slide detection demo:")
    print("    python backend/test_demo.py <video_path>")
    print("\n  - For API server (coming soon):")
    print("    python backend/main.py")
    print("\n\ud83d\udcda Documentation:")
    print("  See README.md for full documentation")
    print("=" * 60)


if __name__ == "__main__":
    main()
