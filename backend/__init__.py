"""
AI Interview Judge - Backend Package

This package contains the backend implementation for the AI Interview Judge system,
including API endpoints, business logic, and service integrations.

Modules:
    - main: FastAPI application and API endpoints
    - core: Core functionality and configuration
    - services: Business logic and service layer
    - test_demo: Command-line demo for slide detection

Author: bigalex95
Version: 0.1.0
"""

__version__ = "0.1.0"
__author__ = "bigalex95"

from backend.core.config import settings

__all__ = ["settings"]
