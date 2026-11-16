#!/bin/bash

# 🚀 Quick-start script for AI Interview Judge

set -e

# Determine the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "🤖 AI Interview Judge - Quick Start"
echo "===================================="
echo ""

# Determine the launch mode
MODE=${1:-cpu}

if [ "$MODE" == "gpu" ]; then
    echo "⚡ Starting the GPU version..."
    PROFILE="--profile gpu"
    SERVICES="ai-judge-gpu frontend-gpu"
else
    echo "💻 Starting the CPU version..."
    PROFILE=""
    SERVICES="ai-judge-cpu frontend"
fi

echo ""
echo "📦 Building images..."
docker compose $PROFILE build

echo ""
echo "🚀 Starting services..."
docker compose $PROFILE up -d $SERVICES

echo ""
echo "⏳ Waiting for services to become ready..."

# Wait for the backend healthcheck
if [ "$MODE" == "gpu" ]; then
    BACKEND="ai-judge-gpu"
else
    BACKEND="ai-judge-cpu"
fi

for i in {1..30}; do
    if docker inspect $BACKEND | grep -q '"Status": "healthy"'; then
        echo "✅ Backend is ready!"
        break
    fi
    echo -n "."
    sleep 2
done

echo ""
echo "🎉 System is up!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 Frontend (Streamlit): http://localhost:8501"
echo "🔧 Backend API:          http://localhost:8000"
echo "📚 API Docs:             http://localhost:8000/docs"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 Useful commands:"
echo "  docker compose logs -f              # Show logs of all services"
echo "  docker compose logs -f frontend     # Frontend logs"
echo "  docker compose logs -f $BACKEND     # Backend logs"
echo "  docker compose down                 # Stop all services"
echo "  docker compose restart frontend     # Restart the frontend"
echo ""
echo "🎯 Open in the browser: http://localhost:8501"
