# ==========================================
# Stage 1: Builder (Compiling C++ Core)
# ==========================================
FROM python:3.11-slim AS builder

# Устанавливаем инструменты для сборки (GCC, CMake, OpenCV Dev)
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    libopencv-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем конфигурацию сборки
COPY CMakeLists.txt .
COPY cpp_core/ ./cpp_core/

# Запускаем сборку C++ модуля
# Результат (.so файл) окажется в /app/libs (как прописано в CMakeLists.txt)
RUN mkdir build && cd build && \
    cmake .. && \
    make -j$(nproc)

# ==========================================
# Stage 2: Runtime (Production Image)
# ==========================================
FROM python:3.11-slim

# Устанавливаем системные зависимости для Runtime
# libopencv-dev нужен, так как наш C++ модуль слинкован с системным OpenCV
# ffmpeg - для Whisper/AudioService
# libgomp1 - для OpenMP (нужен Paddle/Torch)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libopencv-dev \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем 'uv' (быстрый менеджер пакетов)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Копируем файлы зависимостей
COPY pyproject.toml uv.lock ./

# Устанавливаем Python библиотеки в системный Python (флаг --system)
# Это уменьшает размер образа, так как не создается лишний venv
RUN uv sync --frozen

# Копируем скомпилированную C++ библиотеку из Stage 1
COPY --from=builder /app/libs /app/libs

# Копируем исходный код бэкенда
COPY backend/ ./backend/

# Pre-download ML models during build (so container doesn't need internet at runtime)
# 1. Download Whisper model
RUN uv run python -c "from faster_whisper import WhisperModel; WhisperModel('base', device='cpu', compute_type='int8')"

# 2. Download PaddleOCR models (detection + recognition)
RUN uv run python -c "from paddleocr import PaddleOCR; ocr = PaddleOCR(use_angle_cls=False, lang='en', use_gpu=False, show_log=False)"

# Создаем временные папки
RUN mkdir -p temp_uploads temp_audio

# --- Настройка окружения ---

# 1. Решение конфликтов библиотек (Torch vs Paddle)
ENV KMP_DUPLICATE_LIB_OK=TRUE
ENV FLAGS_use_mkldnn=0
ENV FLAGS_enable_mkldnn=0
ENV DNNL_VERBOSE=0

# 2. Добавляем путь к нашей C++ либе, чтобы Python мог сделать 'import ai_interview_cpp'
ENV PYTHONPATH=/app:/app/libs

# 3. Отключаем буферизацию логов (чтобы видеть их в реальном времени)
ENV PYTHONUNBUFFERED=1

# Открываем порт
EXPOSE 8000

# Запуск сервера через uv run
CMD ["uv", "run", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]