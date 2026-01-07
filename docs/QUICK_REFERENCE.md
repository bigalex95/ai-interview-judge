# Quick Reference Guide

## Common Commands

### Building

```bash
# Build C++ module
bash scripts/build.sh

# Copy compiled module to libs (if needed)
cp build/cpp_core/ai_interview_cpp*.so libs/
```

### Running

```bash
# Run slide detection demo
python backend/test_demo.py data/videos/your_video.mp4

# Start API server (development)
python backend/main.py

# Start API server (production)
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Testing

```bash
# Run Python tests
pytest tests/python/

# Run with coverage
pytest --cov=backend tests/python/

# Run specific test
pytest tests/python/test_video_service.py
```

### Development

```bash
# Install in development mode
pip install -e ".[dev]"

# Format code
ruff format .

# Lint code
ruff check .

# Type check
mypy backend/
```

## Project Locations

```
Key Files:
├── backend/main.py              # API server entry point
├── backend/test_demo.py         # CLI demo
├── backend/core/config.py       # Configuration
├── backend/services/video_service.py  # Video processing
└── cpp_core/src/slide_detector.cpp    # Core algorithm

Configuration:
├── .env                         # Local environment (create from .env.example)
├── pyproject.toml              # Python dependencies
└── CMakeLists.txt              # C++ build config

Documentation:
├── README.md                    # Project overview
├── DEVELOPER.md                 # Developer guide
├── CONTRIBUTING.md              # Contribution guidelines
└── REFACTORING_SUMMARY.md      # Recent changes
```

## API Endpoints

```
GET  /                          # API info
GET  /health                    # Health check
POST /api/v1/process-video      # Process video (coming soon)
GET  /api/v1/slides/{video_id}  # Get slides (coming soon)
GET  /docs                      # Swagger UI
GET  /redoc                     # ReDoc UI
```

## Configuration

### Environment Variables

```bash
# Application
DEBUG=False
LOG_LEVEL=INFO

# Slide Detection
MIN_SCENE_DURATION=2.0
MIN_AREA_RATIO=0.15

# API
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4
```

### Python Configuration

```python
from backend.core.config import settings

# Access settings
print(settings.MIN_SCENE_DURATION)
print(settings.DATA_DIR)

# Get all settings
config = settings.get_settings_dict()
```

## Troubleshooting

### C++ Module Import Error

```python
# Problem: ImportError: No module named 'ai_interview_cpp'

# Solution:
# 1. Build the module
bash scripts/build.sh

# 2. Check it exists
ls libs/ai_interview_cpp*.so

# 3. Verify Python path
python -c "import sys; print(sys.path)"

# 4. Try importing
python -c "import ai_interview_cpp; print('OK')"
```

### OpenCV Not Found

```bash
# Problem: OpenCV not found during build

# Solution (Ubuntu/Debian):
sudo apt-get install libopencv-dev

# Solution (macOS):
brew install opencv

# Solution (via pip):
pip install opencv-python
```

### Video Processing Fails

```python
# Check video file
import cv2
cap = cv2.VideoCapture("video.mp4")
print(f"Opened: {cap.isOpened()}")
print(f"FPS: {cap.get(cv2.CAP_PROP_FPS)}")
print(f"Frames: {cap.get(cv2.CAP_PROP_FRAME_COUNT)}")
```

## Code Snippets

### Using Video Service

```python
from backend.services.video_service import SlideDetectionService

# Initialize service
service = SlideDetectionService(
    min_scene_duration=2.0,
    min_area_ratio=0.15
)

# Process video
segments = service.process_video("video.mp4")

# Get frame
frame = service.get_frame("video.mp4", frame_index=0)
```

### Custom Configuration

```python
from backend.core.config import Settings

# Override settings
settings = Settings()
settings.MIN_SCENE_DURATION = 3.0
settings.MIN_AREA_RATIO = 0.20
```

### Custom Exception Handling

```python
from backend.core.exceptions import VideoProcessingError
from backend.services.video_service import SlideDetectionService

try:
    service = SlideDetectionService()
    segments = service.process_video("video.mp4")
except VideoProcessingError as e:
    print(f"Processing failed: {e}")
except FileNotFoundError as e:
    print(f"Video not found: {e}")
```

## Performance Tips

1. **Video Resolution**: Automatically downscaled to 1280px width
2. **Frame Skip**: Process every Nth frame (future enhancement)
3. **Batch Processing**: Process multiple videos in parallel
4. **Caching**: Cache edge maps for repeated analysis

## Useful Links

- [OpenCV Docs](https://docs.opencv.org/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [pybind11 Docs](https://pybind11.readthedocs.io/)
- [CMake Tutorial](https://cmake.org/cmake/help/latest/guide/tutorial/index.html)

## Git Workflow

```bash
# Create feature branch
git checkout -b feature/my-feature

# Make changes and commit
git add .
git commit -m "feat: add new feature"

# Push to remote
git push origin feature/my-feature

# Create pull request on GitHub
```

## Contact

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Email**: See profile
