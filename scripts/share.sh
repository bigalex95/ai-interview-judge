#!/bin/bash

# 🌍 Скрипт для публичного sharing AI Interview Judge через ngrok

set -e

# Определяем корневую директорию проекта
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║         🌍 AI Interview Judge - Public Sharing                ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Проверка, запущена ли система
echo "🔍 Проверка локальной системы..."
if ! curl -sf http://localhost:8501 > /dev/null; then
    echo "❌ Frontend не запущен на localhost:8501"
    echo ""
    echo "Запусти сначала систему:"
    echo "  docker compose up -d"
    echo "  или"
    echo "  ./scripts/start.sh"
    echo ""
    exit 1
fi

if ! curl -sf http://localhost:8000/health > /dev/null; then
    echo "⚠️  Backend не отвечает (но продолжаем...)"
fi

echo "✅ Локальная система работает!"
echo ""

# Проверка ngrok
if ! command -v ngrok &> /dev/null; then
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║  📦 ngrok не установлен                                       ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "Установи ngrok:"
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
    echo "  Или скачай с: https://ngrok.com/download"
    echo ""
    echo "После установки:"
    echo "  1. Зарегистрируйся: https://dashboard.ngrok.com/signup"
    echo "  2. Получи authtoken: https://dashboard.ngrok.com/get-started/your-authtoken"
    echo "  3. Настрой: ngrok config add-authtoken YOUR_TOKEN"
    echo "  4. Запусти снова: ./share.sh"
    echo ""
    exit 1
fi

# Проверка конфигурации ngrok
if ! ngrok config check &> /dev/null; then
    echo "⚠️  ngrok не настроен"
    echo ""
    echo "Получи authtoken:"
    echo "  https://dashboard.ngrok.com/get-started/your-authtoken"
    echo ""
    echo "Затем выполни:"
    echo "  ngrok config add-authtoken YOUR_TOKEN"
    echo ""
    exit 1
fi

echo "✅ ngrok установлен и настроен!"
echo ""

# Выбор режима
echo "📋 Выбери режим sharing:"
echo ""
echo "  1) Frontend только (Streamlit UI) - Порт 8501"
echo "  2) Backend только (FastAPI) - Порт 8000"
echo "  3) Оба сервиса (требуется ngrok Pro)"
echo ""
read -p "Выбор (1-3) [по умолчанию: 1]: " choice
choice=${choice:-1}

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  🚀 Запускаем публичный туннель...                            ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

case $choice in
    1)
        echo "📱 Запускаем туннель для Frontend (Streamlit)..."
        echo ""
        echo "🔗 После запуска скопируй Forwarding URL и отправь другу!"
        echo ""
        echo "💡 Совет: ngrok будет работать пока этот терминал открыт."
        echo "   Нажми Ctrl+C чтобы остановить sharing."
        echo ""
        sleep 2
        ngrok http 8501
        ;;
    2)
        echo "🔧 Запускаем туннель для Backend (API)..."
        echo ""
        echo "🔗 После запуска скопируй Forwarding URL"
        echo "   Твой друг сможет использовать API напрямую!"
        echo ""
        sleep 2
        ngrok http 8000
        ;;
    3)
        echo "🌐 Запускаем туннели для обоих сервисов..."
        echo ""
        if [ ! -f "ngrok.yml" ]; then
            echo "⚠️  Создаю конфигурационный файл ngrok.yml..."
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
            echo "✅ Создан ngrok.yml"
        fi
        echo ""
        echo "🔗 Получишь 2 URL - для Frontend и Backend"
        echo ""
        sleep 2
        ngrok start --all --config ngrok.yml
        ;;
    *)
        echo "❌ Неверный выбор"
        exit 1
        ;;
esac

# Этот код выполнится после остановки ngrok (Ctrl+C)
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  👋 Sharing остановлен                                        ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Локальная система все еще работает:"
echo "  http://localhost:8501"
echo ""
