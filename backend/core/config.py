"""
Configuration Management

Central configuration for the AI Interview Judge application.
Uses environment variables with sensible defaults.
"""

import os
from pathlib import Path
from typing import Optional


class Settings:
    """
    Application settings and configuration.

    Attributes:
        PROJECT_ROOT: Root directory of the project
        DATA_DIR: Directory for data storage
        VIDEOS_DIR: Directory for video files
        SLIDES_DIR: Directory for extracted slides
        LOGS_DIR: Directory for log files

        # Slide Detection Settings
        MIN_SCENE_DURATION: Minimum duration between slides (seconds)
        MIN_AREA_RATIO: Minimum area ratio for slide detection

        # API Settings
        API_HOST: API server host
        API_PORT: API server port
        API_WORKERS: Number of API workers

        # Debug Settings
        DEBUG: Enable debug mode
        LOG_LEVEL: Logging level
    """

    # Project paths
    PROJECT_ROOT: Path = Path(__file__).parent.parent.parent
    DATA_DIR: Path = PROJECT_ROOT / "data"
    VIDEOS_DIR: Path = DATA_DIR / "videos"
    SLIDES_DIR: Path = DATA_DIR / "detected_slides"
    IMAGES_DIR: Path = DATA_DIR / "images"
    LOGS_DIR: Path = PROJECT_ROOT / "logs"

    # Slide detection defaults
    MIN_SCENE_DURATION: float = float(os.getenv("MIN_SCENE_DURATION", "2.0"))
    MIN_AREA_RATIO: float = float(os.getenv("MIN_AREA_RATIO", "0.15"))

    # API configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_WORKERS: int = int(os.getenv("API_WORKERS", "4"))

    # Debug and logging
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    @classmethod
    def ensure_directories(cls) -> None:
        """Create necessary directories if they don't exist."""
        for directory in [
            cls.DATA_DIR,
            cls.VIDEOS_DIR,
            cls.SLIDES_DIR,
            cls.IMAGES_DIR,
            cls.LOGS_DIR,
        ]:
            directory.mkdir(parents=True, exist_ok=True)

    @classmethod
    def get_settings_dict(cls) -> dict:
        """
        Get all settings as a dictionary.

        Returns:
            Dictionary containing all configuration settings
        """
        return {
            "project_root": str(cls.PROJECT_ROOT),
            "data_dir": str(cls.DATA_DIR),
            "min_scene_duration": cls.MIN_SCENE_DURATION,
            "min_area_ratio": cls.MIN_AREA_RATIO,
            "api_host": cls.API_HOST,
            "api_port": cls.API_PORT,
            "debug": cls.DEBUG,
            "log_level": cls.LOG_LEVEL,
        }


# Global settings instance
settings = Settings()

# Ensure directories exist
settings.ensure_directories()
