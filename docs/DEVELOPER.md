# Developer Documentation

## Project Overview

AI Interview Judge is a multimodal AI system for automatically evaluating technical interviews and presentations. The system uses a hybrid C++/Python architecture for optimal performance.

## Architecture

### System Components

1. **C++ Core Module** (`cpp_core/`)

   - High-performance video processing
   - Slide detection using OpenCV
   - Edge detection and frame comparison algorithms

2. **Python Backend** (`backend/`)

   - FastAPI REST API
   - Business logic and services
   - Integration with C++ module via pybind11

3. **Frontend** (Coming in future sprints)
   - Web interface for video upload and analysis
   - Results visualization

### Technology Stack

- **Languages**: C++17, Python 3.10+
- **Frameworks**: FastAPI, pybind11
- **Libraries**: OpenCV 4.x, NumPy
- **Build System**: CMake, uv
- **Testing**: pytest, Google Test

## Project Structure

```
ai-interview-judge/
├── backend/                    # Python backend
│   ├── core/                  # Core functionality
│   │   ├── __init__.py
│   │   ├── config.py         # Configuration management
│   │   ├── exceptions.py     # Custom exceptions
│   │   └── logging_config.py # Logging setup
│   ├── services/              # Business logic
│   │   ├── __init__.py
│   │   └── video_service.py  # Video processing service
│   ├── __init__.py
│   ├── main.py               # FastAPI application
│   └── test_demo.py          # CLI demo
├── cpp_core/                  # C++ implementation
│   ├── include/              # Header files
│   │   └── ai_interview/
│   │       └── slide_detector.hpp
│   └── src/                  # Source files
│       ├── bindings.cpp      # Python bindings
│       └── slide_detector.cpp # Slide detection logic
├── data/                      # Data directory
│   ├── images/               # Test images
│   ├── videos/               # Test videos
│   └── detected_slides/      # Output slides
├── scripts/                   # Build and utility scripts
│   └── build.sh              # Build script
├── tests/                     # Test suite
│   ├── cpp/                  # C++ tests
│   └── python/               # Python tests
├── docker/                    # Docker configuration
│   └── Dockerfile.dev        # Development container
├── CMakeLists.txt            # CMake configuration
├── pyproject.toml            # Python project config
├── README.md                 # Project documentation
├── CONTRIBUTING.md           # Contribution guidelines
└── .env.example              # Environment template
```

## Key Concepts

### Slide Detection Algorithm

The slide detection algorithm works as follows:

1. **Preprocessing**: Convert frames to grayscale and apply Gaussian blur
2. **Edge Detection**: Use Canny edge detection to identify structure
3. **Dilation**: Thicken edges to reduce noise sensitivity
4. **Comparison**: Compare edge maps between frames
5. **Change Detection**: Calculate change ratio based on contour areas
6. **Filtering**: Apply time-based and threshold filters

### Configuration

Configuration is managed through:

- Environment variables (`.env` file)
- `backend/core/config.py` - Settings class
- Default constants in C++ headers

### API Endpoints

#### Current Endpoints

- `GET /` - API info and health check
- `GET /health` - Health check for monitoring
- `POST /api/v1/process-video` - Process video (coming soon)
- `GET /api/v1/slides/{video_id}` - Get slides (coming soon)

## Development Workflow

### Building the Project

```bash
# Build C++ module
bash scripts/build.sh

# The compiled module will be in build/cpp_core/
# Copy it to libs/ if needed
cp build/cpp_core/ai_interview_cpp*.so libs/
```

### Running Tests

```bash
# Python tests
pytest tests/python/

# C++ tests (if implemented)
cd build
ctest
```

### Running the Demo

```bash
# Slide detection demo
python backend/test_demo.py data/videos/your_video.mp4
```

### Starting the API Server

```bash
# Development server with hot-reload
python backend/main.py

# Or using uvicorn directly
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

## Code Standards

### Python

- Use type hints for all function signatures
- Write comprehensive docstrings (Google style)
- Follow PEP 8 style guide
- Use `ruff` for linting and formatting
- Maximum line length: 100 characters

Example:

```python
def process_video(video_path: str, min_duration: float = 2.0) -> List[Dict[str, Any]]:
    """
    Process a video file to detect slide transitions.

    Args:
        video_path: Path to the video file
        min_duration: Minimum duration between slides

    Returns:
        List of detected slide segments

    Raises:
        VideoProcessingError: If processing fails
    """
    pass
```

### C++

- Follow Google C++ Style Guide
- Use meaningful names
- Comment complex algorithms
- Use `const` where appropriate
- Prefer RAII for resource management

Example:

```cpp
/**
 * @brief Process video and detect slide transitions.
 *
 * @param video_path Path to the video file
 * @return std::vector<SlideSegment> Detected slides
 * @throws std::runtime_error If video cannot be opened
 */
std::vector<SlideSegment> process_video(const std::string& video_path);
```

## Performance Considerations

- C++ module handles computationally intensive tasks
- Frame resizing reduces processing time for high-resolution videos
- Edge maps are compared against reference frame, not every frame
- Configurable frame skip for further optimization (future enhancement)

## Debugging

### Enable Debug Logging

```bash
export DEBUG=True
export LOG_LEVEL=DEBUG
python backend/main.py
```

### C++ Module Issues

If the C++ module fails to import:

1. Check that it's built: `ls libs/ai_interview_cpp*`
2. Verify Python can find it: `python -c "import ai_interview_cpp; print('OK')"`
3. Check OpenCV installation: `python -c "import cv2; print(cv2.__version__)"`

## Future Enhancements

- [ ] Audio transcription with Whisper
- [ ] OCR for slide text extraction
- [ ] LLM-based interview evaluation
- [ ] Web frontend
- [ ] Real-time processing
- [ ] Multi-language support
- [ ] Advanced analytics and reporting

## Resources

- [OpenCV Documentation](https://docs.opencv.org/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [pybind11 Documentation](https://pybind11.readthedocs.io/)
- [CMake Documentation](https://cmake.org/documentation/)

## Support

For questions and issues:

- GitHub Issues: Report bugs and feature requests
- Documentation: Check README.md and this file
- Code Comments: Inline documentation in source files
