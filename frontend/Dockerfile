# Use a lightweight Python image
FROM python:3.10-slim

WORKDIR /app

# Install curl for the healthcheck, plus dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && pip install streamlit requests watchdog

# Copy the application code
COPY app.py .

# Expose the Streamlit port (8501 by default)
EXPOSE 8501

# Container healthcheck
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Run the application
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]