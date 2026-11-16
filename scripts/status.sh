#!/bin/bash

# 🔍 Status check script for AI Interview Judge

# Determine the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║         🤖 AI Interview Judge - System Status                  ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check Docker Compose
echo "📦 Checking containers..."
docker compose ps
echo ""

# Check Frontend
echo "🌐 Checking Frontend (http://localhost:8501)..."
if curl -sf http://localhost:8501 > /dev/null; then
    echo "✅ Frontend is running!"
else
    echo "❌ Frontend is not responding"
    echo "   Try: docker compose logs frontend"
fi
echo ""

# Check Backend
echo "🔧 Checking Backend (http://localhost:8000)..."
if curl -sf http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is running!"
    curl -s http://localhost:8000/health | python3 -m json.tool
else
    echo "❌ Backend is not responding"
    echo "   Try: docker compose logs ai-judge-cpu"
fi
echo ""

# Useful commands
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  📋 Useful commands:                                         ║"
echo "║                                                                ║"
echo "║  docker compose logs -f frontend    # Frontend logs          ║"
echo "║  docker compose logs -f ai-judge-cpu # Backend logs           ║"
echo "║  docker compose restart frontend    # Restart the frontend    ║"
echo "║  docker compose down                # Stop everything         ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Links
echo "🌐 Open in the browser:"
echo "   Frontend:  http://localhost:8501"
echo "   API Docs:  http://localhost:8000/docs"
echo ""
