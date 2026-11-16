#!/bin/bash

# 🌩️ Script for public sharing via Cloudflare Tunnel
# A free ngrok alternative with no traffic limits

set -e

# Determine the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║      🌩️  Cloudflare Tunnel - Free Public Access           ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# System check
echo "🔍 Checking the local system..."
if ! curl -sf http://localhost:8501 > /dev/null; then
    echo "❌ Frontend is not running on localhost:8501"
    echo "   Run: docker compose up -d"
    exit 1
fi

echo "✅ System is running!"
echo ""

# Check cloudflared
if ! command -v cloudflared &> /dev/null; then
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║  📦 cloudflared is not installed                             ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "Install cloudflared:"
    echo ""
    echo "  macOS (Homebrew):"
    echo "    brew install cloudflare/cloudflare/cloudflared"
    echo ""
    echo "  Linux (Ubuntu/Debian):"
    echo "    wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb"
    echo "    sudo dpkg -i cloudflared-linux-amd64.deb"
    echo ""
    echo "  Or download from: https://github.com/cloudflare/cloudflared/releases"
    echo ""
    exit 1
fi

echo "✅ cloudflared is installed!"
echo ""

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  🚀 Starting Cloudflare Tunnel...                             ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Cloudflare Tunnel advantages:"
echo "  ✅ Completely free"
echo "  ✅ No traffic limits"
echo "  ✅ Temporary URL (no sign-up)"
echo "  ✅ Automatic HTTPS"
echo ""
echo "🔗 You will get a URL like: https://xxx.trycloudflare.com"
echo ""
echo "💡 Tip: the URL works while this terminal stays open."
echo "   Press Ctrl+C to stop."
echo ""

sleep 2

# Start a quick tunnel (no configuration)
cloudflared tunnel --url http://localhost:8501

# After it stops
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  👋 Tunnel stopped                                            ║"
echo "╚════════════════════════════════════════════════════════════════╝"
