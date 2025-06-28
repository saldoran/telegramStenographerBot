#!/usr/bin/env python3
"""
Telegram Stenographer Bot
Основной файл запуска бота-стенографа для отслеживания сообщений пользователей
"""

import asyncio
import logging
import os
from dotenv import load_dotenv

from bot.stenographer_bot import StenographerBot
from database.database_manager import DatabaseManager

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def main():
    """Главная функция запуска бота"""
    # Получаем токен бота из переменных окружения
    bot_token = os.getenv('BOT_TOKEN')
    if not bot_token:
        logger.error("BOT_TOKEN не найден в переменных окружения!")
        return
    
    # Получаем ID администратора
    admin_user_id = os.getenv('ADMIN_USER_ID')
    if not admin_user_id:
        logger.error("ADMIN_USER_ID не найден в переменных окружения!")
        return
    
    try:
        admin_user_id = int(admin_user_id)
    except ValueError:
        logger.error("ADMIN_USER_ID должен быть числом!")
        return
    
    # Инициализируем базу данных
    db_manager = DatabaseManager()
    await db_manager.init_database()
    
    # Создаем и запускаем бота
    bot = StenographerBot(bot_token, admin_user_id, db_manager)
    
    logger.info("🤖 Запуск Telegram Stenographer Bot...")
    try:
        await bot.run()
    except KeyboardInterrupt:
        logger.info("❌ Получен сигнал завершения. Останавливаем бота...")
    except Exception as e:
        logger.error(f"❌ Ошибка при работе бота: {e}")
    finally:
        await db_manager.close()
        logger.info("✅ Бот остановлен")


if __name__ == "__main__":
    asyncio.run(main())
