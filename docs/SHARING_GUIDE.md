# Sharing AI Interview Judge Over the Internet

The app runs on your machine (frontend on port 8501, backend on port 8000). To let someone else try it, expose the frontend through a tunnel. Start the system first (`./scripts/start.sh` or `docker compose up -d`).

## Option 1: ngrok (`scripts/share.sh`)

```bash
ngrok config add-authtoken YOUR_AUTH_TOKEN   # once, after signing up at ngrok.com
./scripts/share.sh                           # interactive: frontend, backend, or both
# or directly:
ngrok http 8501
```

You get a URL like `https://abcd-1234.ngrok-free.app`. On the free plan the URL changes on every restart and traffic is limited.

## Option 2: Cloudflare Tunnel (`scripts/share-cloudflare.sh`)

```bash
./scripts/share-cloudflare.sh
# or directly:
cloudflared tunnel --url http://localhost:8501
```

A temporary `https://xxx.trycloudflare.com` URL is created without sign-up. It works while the terminal stays open. A named tunnel with your own domain requires a Cloudflare account (`cloudflared tunnel login`, `cloudflared tunnel create ai-judge`).

## Option 3: LocalTunnel

```bash
npm install -g localtunnel
lt --port 8501 --subdomain my-ai-judge
```

Quick and requires no sign-up, but less stable, and it shows a warning page on first visit.

## Option 4: Permanent hosting

For a permanent deployment, host the backend on a container platform (Railway, Render, DigitalOcean App Platform, Google Cloud Run) using `docker-compose.yml`/`docker/Dockerfile.cpu`. The Streamlit frontend can be deployed separately on [Streamlit Community Cloud](https://share.streamlit.io); set `API_URL` to the backend's public URL.

## Security notes

1. Keep `.env` (API keys) out of version control and out of images that you publish.
2. A public URL lets anyone upload videos and spend your LLM API credits. Add a simple password gate to the Streamlit app, or restrict access (for example Cloudflare Access).
3. Interview videos and logs may contain personal data; do not leave tunnels open longer than needed.
