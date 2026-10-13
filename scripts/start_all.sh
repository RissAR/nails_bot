#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$DIR"

echo "=== Запуск Sense Nail Studio (Tunnel + Backend + Bot) ==="

# 1. Запуск Cloudflare Tunnel
echo "Запуск Cloudflare Tunnel..."
cloudflared tunnel --url http://localhost:8000 --no-autoupdate --logfile tunnel.log > /dev/null 2>&1 &
TUNNEL_PID=$!
echo "Tunnel PID: $TUNNEL_PID. Очікування отримання HTTPS URL..."

TUNNEL_URL=""
for i in {1..20}; do
    sleep 1
    if [ -f tunnel.log ]; then
        TUNNEL_URL=$(grep -o 'https://.*\.trycloudflare\.com' tunnel.log | head -n 1 || true)
        if [ -n "$TUNNEL_URL" ]; then
            break
        fi
    fi
done

if [ -n "$TUNNEL_URL" ]; then
    echo "Отримано HTTPS URL: $TUNNEL_URL"
    # Оновлення WEBAPP_URL в .env
    if grep -q "^WEBAPP_URL=" .env; then
        sed -i "s|^WEBAPP_URL=.*|WEBAPP_URL=${TUNNEL_URL}/app|" .env
    else
        echo "WEBAPP_URL=${TUNNEL_URL}/app" >> .env
    fi
    echo "Оновлено WEBAPP_URL у .env: ${TUNNEL_URL}/app"
else
    echo "Увага: Не вдалося отримати trycloudflare URL. Використовується поточний .env"
fi

# 2. Запуск Bot + FastAPI
echo "Запуск FastAPI та Telegram Bot..."
.venv/bin/python -m src.main
