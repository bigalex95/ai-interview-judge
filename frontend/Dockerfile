# Используем легкий Python образ
FROM python:3.10-slim

WORKDIR /app

# Устанавливаем curl для healthcheck и зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && pip install streamlit requests watchdog

# Копируем код приложения
COPY app.py .

# Открываем порт Streamlit (по умолчанию 8501)
EXPOSE 8501

# Healthcheck для контейнера
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Запускаем приложение
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]