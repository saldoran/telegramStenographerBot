# Makefile для управления Telegram Stenographer Bot

.PHONY: help install run test clean stats config

# Показать справку
help:
	@echo "🤖 Telegram Stenographer Bot - команды управления"
	@echo ""
	@echo "Доступные команды:"
	@echo "  make install   - установить зависимости"
	@echo "  make run       - запустить бота"
	@echo "  make test      - запустить тесты (если есть)"
	@echo "  make clean     - очистить временные файлы"
	@echo "  make stats     - показать статистику"
	@echo "  make config    - проверить конфигурацию"

# Установка зависимостей
install:
	@echo "📦 Установка зависимостей..."
	python3 -m venv venv
	venv/bin/pip install -r requirements.txt
	@echo "✅ Зависимости установлены"

# Запуск бота
run:
	@echo "🤖 Запуск бота..."
	./run_bot.sh

# Тестирование (пока что просто проверка синтаксиса)
test:
	@echo "🧪 Проверка синтаксиса..."
	venv/bin/python -m py_compile main.py
	venv/bin/python -m py_compile bot/stenographer_bot.py
	venv/bin/python -m py_compile database/database_manager.py
	venv/bin/python -m py_compile handlers/admin_handlers.py
	venv/bin/python -m py_compile handlers/message_handlers.py
	venv/bin/python -m py_compile utils/file_handler.py
	@echo "✅ Синтаксис корректен"

# Очистка временных файлов
clean:
	@echo "🧹 Очистка временных файлов..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	@echo "✅ Временные файлы очищены"

# Показать статистику
stats:
	@echo "📊 Показываем статистику..."
	venv/bin/python tools.py stats

# Проверить конфигурацию
config:
	@echo "🔧 Проверяем конфигурацию..."
	venv/bin/python tools.py config
