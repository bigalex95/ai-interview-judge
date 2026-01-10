#!/bin/bash

# 🌩️ Скрипт для публичного sharing через Cloudflare Tunnel
# Бесплатная альтернатива ngrok без ограничений трафика

set -e

# Определяем корневую директорию проекта
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║      🌩️  Cloudflare Tunnel - Бесплатный Public Access        ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Проверка системы
echo "🔍 Проверка локальной системы..."
if ! curl -sf http://localhost:8501 > /dev/null; then
    echo "❌ Frontend не запущен на localhost:8501"
    echo "   Запусти: docker compose up -d"
    exit 1
fi

echo "✅ Система работает!"
echo ""

# Проверка cloudflared
if ! command -v cloudflared &> /dev/null; then
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║  📦 cloudflared не установлен                                 ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "Установи cloudflared:"
    echo ""
    echo "  macOS (Homebrew):"
    echo "    brew install cloudflare/cloudflare/cloudflared"
    echo ""
    echo "  Linux (Ubuntu/Debian):"
    echo "    wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb"
    echo "    sudo dpkg -i cloudflared-linux-amd64.deb"
    echo ""
    echo "  Или скачай с: https://github.com/cloudflare/cloudflared/releases"
    echo ""
    exit 1
fi

echo "✅ cloudflared установлен!"
echo ""

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  🚀 Запускаем Cloudflare Tunnel...                            ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Преимущества Cloudflare Tunnel:"
echo "  ✅ Полностью бесплатно"
echo "  ✅ Без ограничений трафика"
echo "  ✅ Временный URL (без регистрации)"
echo "  ✅ HTTPS автоматически"
echo ""
echo "🔗 Получишь URL типа: https://xxx.trycloudflare.com"
echo ""
echo "💡 Совет: URL будет работать пока терминал открыт."
echo "   Нажми Ctrl+C чтобы остановить."
echo ""

sleep 2

# Запуск quick tunnel (без конфигурации)
cloudflared tunnel --url http://localhost:8501

# После остановки
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  👋 Tunnel остановлен                                         ║"
echo "╚════════════════════════════════════════════════════════════════╝"
