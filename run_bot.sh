#!/bin/bash
# Скрипт для запуска Telegram Stenographer Bot

# Проверяем существование виртуального окружения
if [ ! -d "venv" ]; then
    echo "❌ Виртуальное окружение не найдено!"
    echo "Создайте его командой: python3 -m venv venv"
    exit 1
fi

# Проверяем файл .env
if [ ! -f ".env" ]; then
    echo "❌ Файл .env не найден!"
    echo "Скопируйте .env.example в .env и заполните переменные"
    exit 1
fi

echo "🤖 Запуск Telegram Stenographer Bot..."

# Активируем виртуальное окружение и запускаем бота
source venv/bin/activate
python main.py
