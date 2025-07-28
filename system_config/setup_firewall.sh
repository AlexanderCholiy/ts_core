#!/bin/bash

# Дополнительные порты/приложения, которые хотим разрешить
# Пример: ALLOWED=("80/tcp" "443/tcp" "1234/tcp")
ALLOWED=(
  "8080/tcp"
  "27018/tcp"
)

# Сбросим ufw к дефолтным настройкам (закроет все порты)
sudo ufw --force reset

# По умолчанию блокируем все входящие
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Разрешаем Nginx Full (обычно 80 и 443)
sudo ufw allow 'Nginx Full'

# Разрешаем OpenSSH (обычно 22)
sudo ufw allow OpenSSH

# Разрешаем дополнительные порты из списка ALLOWED
for port in "${ALLOWED[@]}"; do
  sudo ufw allow "$port"
done

# Включаем ufw
sudo ufw --force enable

# Выводим статус
sudo ufw status verbose
