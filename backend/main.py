"""
AI Interview Judge - Backend API Server

FastAPI-based REST API for the AI Interview Judge application.
Provides endpoints for video processing, slide detection, and interview evaluation.

Author: bigalex95
"""

import os
import logging
import shutil
from pathlib import Path

# --- CRITICAL FIX: Library Conflicts (Torch vs Paddle) ---
# Эти флаги ДОЛЖНЫ быть установлены до любых других импортов (особенно Torch/Paddle)
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"  # Разрешаем две копии OpenMP
os.environ["FLAGS_use_mkldnn"] = "0"  # Выключаем MKLDNN в Paddle (конфликтует с Torch)
os.environ["FLAGS_enable_mkldnn"] = "0"  # Дублирующий флаг для надежности
os.environ["DNNL_VERBOSE"] = "0"  # Убираем лишний шум
# ---------------------------------------------------------

import uvicorn
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

# Теперь можно импортировать тяжелые сервисы
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
    """
    Инициализация ML моделей при старте сервера.
    Это занимает время, но позволяет быстро отвечать на запросы.
    """
    global analysis_service
    logger.info("Initializing ML Models...")
    try:
        analysis_service = AnalysisService()
        logger.info("✅ ML Models Ready (Audio + Video + OCR).")
    except Exception as e:
        logger.error(f"❌ Failed to initialize ML models: {e}")
        # Не роняем сервер полностью, чтобы /health работал
        analysis_service = None


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
    """Health check endpoint."""
    status = "healthy" if analysis_service is not None else "degraded"
    return {"status": status, "service": "ai-interview-judge"}


@app.post("/analyze")
async def analyze_video_endpoint(file: UploadFile = File(...)):
    """
    Full End-to-End Analysis:
    1. Upload Video
    2. Extract Audio -> Whisper -> Text
    3. Extract Keyframes (C++) -> PaddleOCR -> Text
    4. Return JSON
    """
    temp_dir = Path("temp_uploads")
    temp_dir.mkdir(exist_ok=True)

    file_path = temp_dir / file.filename

    try:
        # Save uploaded file
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        logger.info(
            f"Received file: {file.filename}, size: {file_path.stat().st_size / 1024 / 1024:.2f} MB"
        )

        if analysis_service is None:
            raise HTTPException(
                status_code=503, detail="ML Models not initialized. Check server logs."
            )

        # Run Analysis
        result = analysis_service.analyze_content(str(file_path))
        return result

    except Exception as exc:
        logger.error(f"Analysis failed: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        # Cleanup
        if file_path.exists():
            file_path.unlink()


def main():
    """Start the FastAPI server."""
    logger.info("Starting AI Interview Judge API server...")
    # workers=1 важно, чтобы модели не грузились в несколько процессов и не съели всю RAM
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        workers=1,
    )


if __name__ == "__main__":
    main()
