#!/bin/bash

# 🔍 Скрипт проверки статуса AI Interview Judge

# Определяем корневую директорию проекта
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║         🤖 AI Interview Judge - Статус Системы                ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Проверка Docker Compose
echo "📦 Проверка контейнеров..."
docker compose ps
echo ""

# Проверка Frontend
echo "🌐 Проверка Frontend (http://localhost:8501)..."
if curl -sf http://localhost:8501 > /dev/null; then
    echo "✅ Frontend работает!"
else
    echo "❌ Frontend не отвечает"
    echo "   Попробуйте: docker compose logs frontend"
fi
echo ""

# Проверка Backend
echo "🔧 Проверка Backend (http://localhost:8000)..."
if curl -sf http://localhost:8000/health > /dev/null; then
    echo "✅ Backend работает!"
    curl -s http://localhost:8000/health | python3 -m json.tool
else
    echo "❌ Backend не отвечает"
    echo "   Попробуйте: docker compose logs ai-judge-cpu"
fi
echo ""

# Полезные команды
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  📋 Полезные команды:                                         ║"
echo "║                                                                ║"
echo "║  docker compose logs -f frontend    # Логи фронтенда          ║"
echo "║  docker compose logs -f ai-judge-cpu # Логи бэкенда           ║"
echo "║  docker compose restart frontend    # Перезапуск фронтенда    ║"
echo "║  docker compose down                # Остановить все          ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Ссылки
echo "🌐 Открыть в браузере:"
echo "   Frontend:  http://localhost:8501"
echo "   API Docs:  http://localhost:8000/docs"
echo ""
