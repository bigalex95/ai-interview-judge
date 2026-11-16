# AI Interview Judge - Frontend (Streamlit)

Web UI for the AI interview evaluation system.

## Quick start

### Docker Compose (recommended)

CPU version (default):

```bash
# From the project root
docker compose up --build
```

Frontend: **http://localhost:8501**, backend API: **http://localhost:8000**

GPU version (requires an NVIDIA GPU):

```bash
docker compose --profile gpu up --build
```

### Local development (without Docker)

```bash
pip install streamlit requests watchdog

# Connects to http://localhost:8000 by default
streamlit run app.py

# Or with a custom backend URL
API_URL=http://your-backend:8000 streamlit run app.py
```

## Features

- Upload an MP4 interview video and preview it in the browser
- Overall interview score (0-10) with color-coded feedback and an AI summary
- Per-question breakdown:
  - Slide text (OCR)
  - Candidate answer (speech-to-text)
  - AI verdict (Correct / Wrong / Partial) with an explanation

## Architecture

```
┌─────────────────┐         ┌──────────────────┐
│   Streamlit UI  │ ──HTTP──▶│  FastAPI Backend │
│  (Frontend)     │         │  (ai-judge-cpu)  │
│  Port: 8501     │◀────────│  Port: 8000      │
└─────────────────┘  JSON   └──────────────────┘
                                     │
                                     ▼
                            ┌─────────────────┐
                            │   AI Services   │
                            │  - Whisper      │
                            │  - PaddleOCR    │
                            │  - LLM Judge    │
                            └─────────────────┘
```

## Configuration

| Variable  | Description     | Default                 |
| --------- | --------------- | ----------------------- |
| `API_URL` | Backend API URL | `http://localhost:8000` |

In Docker Compose this is set to `http://ai-judge-cpu:8000` or `http://ai-judge-gpu:8000`.

## Troubleshooting

### Cannot connect to the backend

1. Check that the backend container is running: `docker ps | grep ai-judge`
2. Check the backend healthcheck: `docker inspect ai-judge-cpu | grep Health`
3. Check the backend logs: `docker logs ai-judge-cpu`

### Request timeout during analysis

The request times out after 300 seconds. For longer videos, raise the timeout in [app.py](app.py):

```python
response = requests.post(API_URL, files=files, timeout=600)  # 10 minutes
```

### Port 8501 is in use

Change the port mapping in `docker-compose.yml`:

```yaml
ports:
  - "8502:8501" # use 8502 instead of 8501
```

## Dependencies

- `streamlit` - web framework
- `requests` - HTTP client for the API
- `watchdog` - file watcher for hot reload

## Roadmap

- [ ] Multiple videos at once
- [ ] Export results to PDF/Excel
- [ ] Analysis history (database)
- [ ] LLM parameters configurable from the UI
- [ ] Multilingual UI

## License

See [LICENSE](../LICENSE) in the project root.
