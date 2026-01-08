"""
AI Interview Judge - Backend API Server

FastAPI-based REST API for the AI Interview Judge application.
Provides endpoints for video processing, slide detection, and interview evaluation.

Author: bigalex95
"""

import os

# Fix for OpenMP conflict (common in PyTorch/Paddle + FastAPI)
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import logging
import shutil
from pathlib import Path

import uvicorn
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from backend.services.analysis_service import AnalysisService

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

# Global singleton for heavy models
analysis_service: AnalysisService | None = None


@app.on_event("startup")
def startup_event():
    global analysis_service
    logger.info("Initializing ML Models...")
    analysis_service = AnalysisService()
    logger.info("ML Models Ready.")


@app.get("/")
async def root():
    """Root endpoint - API health check and info."""
    return {
        "status": "AI Judge is running",
        "service": "AI Interview Judge API",
        "version": "0.1.0",
        "docs": "/docs",
        "models_loaded": analysis_service is not None,
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.

    Returns:
        JSON response with health status
    """
    return {"status": "healthy", "service": "ai-interview-judge"}


@app.post("/analyze")
async def analyze_video_endpoint(file: UploadFile = File(...)):
    """Upload a video file and get multimodal analysis (text + audio)."""
    temp_dir = Path("temp_uploads")
    temp_dir.mkdir(exist_ok=True)

    file_path = temp_dir / file.filename

    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Could not save file: {exc}")

    try:
        if analysis_service is None:
            raise RuntimeError("Analysis service not initialized")

        result = analysis_service.analyze_content(str(file_path))
        return result
    except Exception as exc:
        logger.error("Analysis failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        # Optionally delete uploaded file after processing
        # file_path.unlink(missing_ok=True)
        pass


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
