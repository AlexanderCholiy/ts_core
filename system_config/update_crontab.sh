#!/bin/bash

CRON_FILE="/etc/crontab"
CRON_SCRIPT_PATH="/home/vostokuser/ts_core/system_config/shutdown_counter.sh"
CRON_COMMAND="* * * * * root ${CRON_SCRIPT_PATH} > /dev/null 2>&1"

# Проверяем, существует ли скрипт
if [ ! -f "$CRON_SCRIPT_PATH" ]; then
    echo "❌ Скрипт $CRON_SCRIPT_PATH не найден. Добавление в crontab отменено."
    exit 1
fi

# Временный файл для обновления
TMP_FILE="$(mktemp)"

# Проверяем, есть ли уже строка с shutdown_counter.sh
if grep -q "shutdown_counter.sh" "$CRON_FILE"; then
    # Заменяем строку
    sudo sed "s|.*shutdown_counter.sh.*|$CRON_COMMAND|" "$CRON_FILE" > "$TMP_FILE"
    sudo cp "$TMP_FILE" "$CRON_FILE"
    echo "✅ Строка с shutdown_counter.sh обновлена в $CRON_FILE"
else
    # Добавляем строку
    echo "$CRON_COMMAND" | sudo tee -a "$CRON_FILE" > /dev/null
    echo "✅ Строка добавлена в $CRON_FILE"
fi

# Удаляем временный файл
rm -f "$TMP_FILE"
