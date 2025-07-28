#!/bin/bash

set -e

SERVICE_NAME="socat-mongo-proxy"
UNIT_PATH="/etc/systemd/system/${SERVICE_NAME}.service"
UNIT_CONTENT="[Unit]
Description=Socat proxy from Docker to local MongoDB
After=network.target
StartLimitIntervalSec=0

[Service]
Type=simple
ExecStart=/usr/bin/socat TCP-LISTEN:27018,fork TCP:127.0.0.1:27017
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
"

echo "==> Проверка установки socat..."
if ! command -v socat &>/dev/null; then
    echo "Устанавливаю socat..."
    sudo apt update && sudo apt install socat -y
else
    echo "socat уже установлен."
fi

echo "==> Проверка systemd unit-файла..."
if [[ ! -f "$UNIT_PATH" ]] || [[ "$(cat "$UNIT_PATH")" != "$UNIT_CONTENT" ]]; then
    echo "Создаю/обновляю unit-файл $UNIT_PATH..."
    echo "$UNIT_CONTENT" | sudo tee "$UNIT_PATH" > /dev/null
    sudo systemctl daemon-reexec
    sudo systemctl daemon-reload
else
    echo "unit-файл уже актуален."
fi

echo "==> Включение и запуск сервиса $SERVICE_NAME..."
sudo systemctl enable --now "$SERVICE_NAME"

echo "==> Статус сервиса:"
sudo systemctl status "$SERVICE_NAME" --no-pager
