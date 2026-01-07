"""
AI Interview Judge - Backend API Server

FastAPI-based REST API for the AI Interview Judge application.
Provides endpoints for video processing, slide detection, and interview evaluation.

Author: bigalex95
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from typing import List, Optional
import uvicorn
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Interview Judge API",
    description="REST API for automated interview evaluation using multimodal AI",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.get("/")
async def root():
    """
    Root endpoint - API health check and info.

    Returns:
        JSON response with API status and version info
    """
    return {
        "status": "online",
        "service": "AI Interview Judge API",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.

    Returns:
        JSON response with health status
    """
    return {"status": "healthy", "service": "ai-interview-judge"}


@app.post("/api/v1/process-video")
async def process_video_endpoint(
    video: UploadFile = File(...),
    min_scene_duration: float = 2.0,
    min_area_ratio: float = 0.15,
):
    """
    Process a video file to detect slide transitions.

    Args:
        video: Video file to process (multipart/form-data)
        min_scene_duration: Minimum duration between slide changes (seconds)
        min_area_ratio: Minimum area ratio for slide change detection (0.0-1.0)

    Returns:
        JSON response with detected slide segments

    Raises:
        HTTPException: If video processing fails
    """
    # TODO: Implement video processing logic
    # This will integrate with the C++ slide detector module
    logger.info(f"Received video: {video.filename}")

    return JSONResponse(
        status_code=501,
        content={
            "error": "Not Implemented",
            "message": "Video processing endpoint coming soon. Use backend/test_demo.py for now.",
        },
    )


@app.get("/api/v1/slides/{video_id}")
async def get_slides(video_id: str):
    """
    Retrieve detected slides for a processed video.

    Args:
        video_id: Unique identifier for the video

    Returns:
        JSON response with slide information

    Raises:
        HTTPException: If video not found or not processed
    """
    # TODO: Implement slide retrieval logic
    logger.info(f"Requesting slides for video: {video_id}")

    return JSONResponse(
        status_code=501,
        content={
            "error": "Not Implemented",
            "message": "Slide retrieval endpoint coming soon.",
        },
    )


def main():
    """
    Start the FastAPI server.

    Runs the uvicorn server with hot-reload enabled for development.
    """
    logger.info("Starting AI Interview Judge API server...")
    uvicorn.run(
        "backend.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info"
    )


if __name__ == "__main__":
    main()
