"""
Custom Exceptions

Application-specific exception classes for better error handling.
"""


class AIInterviewJudgeException(Exception):
    """Base exception for all AI Interview Judge errors."""

    pass


class VideoProcessingError(AIInterviewJudgeException):
    """Raised when video processing fails."""

    pass


class SlideDetectionError(AIInterviewJudgeException):
    """Raised when slide detection fails."""

    pass


class ConfigurationError(AIInterviewJudgeException):
    """Raised when there's a configuration issue."""

    pass


class ModuleNotFoundError(AIInterviewJudgeException):
    """Raised when required module (e.g., C++ module) is not found."""

    pass


class InvalidVideoError(AIInterviewJudgeException):
    """Raised when video file is invalid or corrupted."""

    pass
