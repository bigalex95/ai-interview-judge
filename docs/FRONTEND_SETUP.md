# Running AI Interview Judge with the Streamlit Frontend

## Option 1: Quick-start script (recommended)

```bash
# CPU version
./scripts/start.sh

# GPU version
./scripts/start.sh gpu
```

## Option 2: Docker Compose

CPU version:

```bash
docker compose up --build        # build and run
docker compose up --build -d     # run in the background
docker compose logs -f           # follow logs
```

GPU version:

```bash
docker compose --profile gpu up --build
```

## Option 3: Local development (without Docker)

Start the backend from the project root, then the frontend in another terminal:

```bash
uvicorn backend.main:app --reload --port 8000
```

```bash
cd frontend
pip install streamlit requests watchdog
streamlit run app.py
```

## Architecture

```
┌─────────────────────────────────────────────┐
│          Docker Compose Network             │
│         (ai-judge-network)                  │
│                                             │
│  ┌──────────────────┐  ┌─────────────────┐ │
│  │   Frontend       │  │   Backend       │ │
│  │   (Streamlit)    │──▶   (FastAPI)     │ │
│  │   Port: 8501     │  │   Port: 8000    │ │
│  └──────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────┘
     http://localhost:8501  http://localhost:8000
```

## Troubleshooting

### Frontend cannot connect to the backend

```bash
docker compose ps                                  # container status
docker compose logs ai-judge-cpu                   # backend logs
docker inspect ai-judge-cpu | grep -A 10 Health    # healthcheck
docker compose restart ai-judge-cpu                # restart the backend
```

### Image build fails with a network error

Example: `failed to resolve source metadata for ghcr.io/astral-sh/uv:latest: dial tcp: lookup ghcr.io ... i/o timeout`.

- Check connectivity: `ping ghcr.io`
- Try a different DNS server, or run the backend locally (Option 3).
- If the build hangs: `export DOCKER_BUILDKIT=1`, or rebuild from scratch with `docker compose build --no-cache`.

## Useful commands

```bash
docker compose logs -f frontend
docker compose restart frontend
docker compose down
docker compose down -v          # also remove volumes
```
