#!/bin/bash

# 🌍 Script for public sharing of AI Interview Judge via ngrok

set -e

# Determine the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║         🌍 AI Interview Judge - Public Sharing                ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check that the system is running
echo "🔍 Checking the local system..."
if ! curl -sf http://localhost:8501 > /dev/null; then
    echo "❌ Frontend is not running on localhost:8501"
    echo ""
    echo "Start the system first:"
    echo "  docker compose up -d"
    echo "  or"
    echo "  ./scripts/start.sh"
    echo ""
    exit 1
fi

if ! curl -sf http://localhost:8000/health > /dev/null; then
    echo "⚠️  Backend is not responding (continuing anyway...)"
fi

echo "✅ Local system is running!"
echo ""

# Check ngrok
if ! command -v ngrok &> /dev/null; then
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║  📦 ngrok is not installed                                   ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "Install ngrok:"
    echo ""
    echo "  macOS (Homebrew):"
    echo "    brew install ngrok/ngrok/ngrok"
    echo ""
    echo "  Linux:"
    echo "    curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | \\"
    echo "      sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null"
    echo "    echo 'deb https://ngrok-agent.s3.amazonaws.com buster main' | \\"
    echo "      sudo tee /etc/apt/sources.list.d/ngrok.list"
    echo "    sudo apt update && sudo apt install ngrok"
    echo ""
    echo "  Or download from: https://ngrok.com/download"
    echo ""
    echo "After installing:"
    echo "  1. Sign up: https://dashboard.ngrok.com/signup"
    echo "  2. Get an authtoken: https://dashboard.ngrok.com/get-started/your-authtoken"
    echo "  3. Configure: ngrok config add-authtoken YOUR_TOKEN"
    echo "  4. Run again: ./share.sh"
    echo ""
    exit 1
fi

# Check the ngrok configuration
if ! ngrok config check &> /dev/null; then
    echo "⚠️  ngrok is not configured"
    echo ""
    echo "Get an authtoken:"
    echo "  https://dashboard.ngrok.com/get-started/your-authtoken"
    echo ""
    echo "Then run:"
    echo "  ngrok config add-authtoken YOUR_TOKEN"
    echo ""
    exit 1
fi

echo "✅ ngrok is installed and configured!"
echo ""

# Mode selection
echo "📋 Choose a sharing mode:"
echo ""
echo "  1) Frontend only (Streamlit UI) - port 8501"
echo "  2) Backend only (FastAPI) - port 8000"
echo "  3) Both services (requires ngrok Pro)"
echo ""
read -p "Choice (1-3) [default: 1]: " choice
choice=${choice:-1}

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  🚀 Starting the public tunnel...                             ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

case $choice in
    1)
        echo "📱 Starting a tunnel for the Frontend (Streamlit)..."
        echo ""
        echo "🔗 After startup, copy the Forwarding URL and share it!"
        echo ""
        echo "💡 Tip: ngrok works while this terminal stays open."
        echo "   Press Ctrl+C to stop sharing."
        echo ""
        sleep 2
        ngrok http 8501
        ;;
    2)
        echo "🔧 Starting a tunnel for the Backend (API)..."
        echo ""
        echo "🔗 After startup, copy the Forwarding URL"
        echo "   Others will be able to use the API directly!"
        echo ""
        sleep 2
        ngrok http 8000
        ;;
    3)
        echo "🌐 Starting tunnels for both services..."
        echo ""
        if [ ! -f "ngrok.yml" ]; then
            echo "⚠️  Creating the ngrok.yml config file..."
            cat > ngrok.yml << 'EOF'
version: "2"
tunnels:
  frontend:
    proto: http
    addr: 8501
    inspect: true
  backend:
    proto: http
    addr: 8000
    inspect: true
EOF
            echo "✅ Created ngrok.yml"
        fi
        echo ""
        echo "🔗 You will get 2 URLs - one for the Frontend, one for the Backend"
        echo ""
        sleep 2
        ngrok start --all --config ngrok.yml
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

# This runs after ngrok is stopped (Ctrl+C)
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  👋 Sharing stopped                                           ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "The local system is still running:"
echo "  http://localhost:8501"
echo ""
