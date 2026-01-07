# Contributing Guidelines

Thank you for your interest in contributing to AI Interview Judge! This document provides guidelines and instructions for contributing to the project.

## Development Setup

### Prerequisites

- Python 3.10 or higher
- C++ compiler (GCC/Clang/MSVC)
- CMake 3.10 or higher
- OpenCV 4.x
- Git

### Setting Up Development Environment

1. Clone the repository:

```bash
git clone https://github.com/bigalex95/ai-interview-judge.git
cd ai-interview-judge
```

2. Install Python dependencies:

```bash
pip install -e ".[dev]"
```

3. Build the C++ module:

```bash
bash scripts/build.sh
```

4. Run tests:

```bash
pytest tests/python/
```

## Code Style

### Python

- Follow PEP 8 style guide
- Use type hints for function signatures
- Write docstrings for all public functions and classes
- Maximum line length: 100 characters
- Use `ruff` for linting and formatting

### C++

- Follow Google C++ Style Guide
- Use meaningful variable and function names
- Comment complex algorithms
- Keep functions focused and small

## Testing

- Write tests for all new features
- Ensure all tests pass before submitting PR
- Aim for high test coverage

## Pull Request Process

1. Fork the repository
2. Create a feature branch from `main`
3. Make your changes
4. Add tests for new functionality
5. Update documentation as needed
6. Submit a pull request

## Code Review

All submissions require review. We use GitHub pull requests for this purpose.

## Reporting Issues

Use GitHub Issues to report bugs or suggest features. Please include:

- Clear description of the issue
- Steps to reproduce (for bugs)
- Expected vs actual behavior
- System information (OS, Python version, etc.)

## License

By contributing, you agree that your contributions will be licensed under the project's license.
