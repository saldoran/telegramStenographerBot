#!/usr/bin/env python3
"""
Утилита для управления базой данных и настройками бота
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Добавляем корневую директорию в PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

from database.database_manager import DatabaseManager

load_dotenv()


async def show_stats():
    """Показать статистику базы данных"""
    db_manager = DatabaseManager()
    await db_manager.init_database()
    
    print("📊 Статистика Telegram Stenographer Bot")
    print("=" * 50)
    
    # Статистика пользователей
    users = await db_manager.get_tracked_users()
    print(f"👥 Отслеживаемых пользователей: {len(users)}")
    
    if users:
        print("\n📋 Список пользователей:")
        for i, user in enumerate(users, 1):
            user_info = f"{i}. ID: {user['user_id']}"
            if user['username']:
                user_info += f" (@{user['username']})"
            if user['first_name']:
                user_info += f" - {user['first_name']}"
                if user['last_name']:
                    user_info += f" {user['last_name']}"
            print(f"   {user_info}")
    
    await db_manager.close()


async def clear_database():
    """Очистить базу данных"""
    response = input("⚠️ Вы уверены, что хотите очистить базу данных? (yes/no): ")
    if response.lower() != 'yes':
        print("❌ Операция отменена")
        return
    
    db_path = "stenographer.db"
    if os.path.exists(db_path):
        os.remove(db_path)
        print("✅ База данных очищена")
    else:
        print("ℹ️ База данных не найдена")


def check_config():
    """Проверить конфигурацию"""
    print("🔧 Проверка конфигурации...")
    print("=" * 30)
    
    # Проверяем .env файл
    if not os.path.exists('.env'):
        print("❌ Файл .env не найден!")
        print("💡 Скопируйте .env.example в .env и заполните переменные")
        return False
    
    # Проверяем переменные окружения
    bot_token = os.getenv('BOT_TOKEN')
    admin_user_id = os.getenv('ADMIN_USER_ID')
    
    if not bot_token:
        print("❌ BOT_TOKEN не указан в .env")
        return False
    else:
        print("✅ BOT_TOKEN найден")
    
    if not admin_user_id:
        print("❌ ADMIN_USER_ID не указан в .env")
        return False
    else:
        try:
            int(admin_user_id)
            print("✅ ADMIN_USER_ID найден и корректен")
        except ValueError:
            print("❌ ADMIN_USER_ID должен быть числом")
            return False
    
    # Проверяем виртуальное окружение
    if os.path.exists('venv'):
        print("✅ Виртуальное окружение найдено")
    else:
        print("⚠️ Виртуальное окружение не найдено")
        print("💡 Создайте его: python3 -m venv venv")
    
    print("\n✅ Конфигурация корректна!")
    return True


def main():
    """Главная функция"""
    if len(sys.argv) < 2:
        print("🛠️ Утилита управления Telegram Stenographer Bot")
        print("\nДоступные команды:")
        print("  python tools.py stats     - показать статистику")
        print("  python tools.py clear     - очистить базу данных")
        print("  python tools.py config    - проверить конфигурацию")
        print("  python tools.py help      - показать эту справку")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'stats':
        asyncio.run(show_stats())
    elif command == 'clear':
        asyncio.run(clear_database())
    elif command == 'config':
        check_config()
    elif command == 'help':
        main()
    else:
        print(f"❌ Неизвестная команда: {command}")
        main()


if __name__ == "__main__":
    main()
