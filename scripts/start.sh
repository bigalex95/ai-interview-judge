#!/bin/bash

# 🚀 Скрипт быстрого запуска AI Interview Judge

set -e

# Определяем корневую директорию проекта
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "🤖 AI Interview Judge - Quick Start"
echo "===================================="
echo ""

# Определяем режим запуска
MODE=${1:-cpu}

if [ "$MODE" == "gpu" ]; then
    echo "⚡ Запускаем GPU версию..."
    PROFILE="--profile gpu"
    SERVICES="ai-judge-gpu frontend-gpu"
else
    echo "💻 Запускаем CPU версию..."
    PROFILE=""
    SERVICES="ai-judge-cpu frontend"
fi

echo ""
echo "📦 Сборка образов..."
docker compose $PROFILE build

echo ""
echo "🚀 Запускаем сервисы..."
docker compose $PROFILE up -d $SERVICES

echo ""
echo "⏳ Ожидаем готовности сервисов..."

# Ждем healthcheck бэкенда
if [ "$MODE" == "gpu" ]; then
    BACKEND="ai-judge-gpu"
else
    BACKEND="ai-judge-cpu"
fi

for i in {1..30}; do
    if docker inspect $BACKEND | grep -q '"Status": "healthy"'; then
        echo "✅ Backend готов!"
        break
    fi
    echo -n "."
    sleep 2
done

echo ""
echo "🎉 Система запущена!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 Frontend (Streamlit): http://localhost:8501"
echo "🔧 Backend API:          http://localhost:8000"
echo "📚 API Docs:             http://localhost:8000/docs"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 Полезные команды:"
echo "  docker compose logs -f              # Показать логи всех сервисов"
echo "  docker compose logs -f frontend     # Логи фронтенда"
echo "  docker compose logs -f $BACKEND     # Логи бэкенда"
echo "  docker compose down                 # Остановить все сервисы"
echo "  docker compose restart frontend     # Перезапустить фронтенд"
echo ""
echo "🎯 Откройте браузер: http://localhost:8501"
