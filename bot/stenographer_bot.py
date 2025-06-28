"""
Основной класс Telegram бота-стенографа
"""

import logging
import os
from typing import Optional, Dict, Any
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from database.database_manager import DatabaseManager
from handlers.admin_handlers import AdminHandlers
from handlers.message_handlers import MessageHandlers
from utils.file_handler import FileHandler

logger = logging.getLogger(__name__)


class StenographerBot:
    """Основной класс бота-стенографа"""
    
    def __init__(self, bot_token: str, admin_user_id: int, db_manager: DatabaseManager):
        self.bot_token = bot_token
        self.admin_user_id = admin_user_id
        self.db_manager = db_manager
        self.file_handler = FileHandler()
        
        # Создаем приложение
        self.application = Application.builder().token(bot_token).build()
        
        # Инициализируем обработчики
        self.admin_handlers = AdminHandlers(db_manager, admin_user_id)
        self.message_handlers = MessageHandlers(db_manager, self.file_handler)
        
        # Регистрируем обработчики
        self._register_handlers()
    
    def _register_handlers(self):
        """Регистрация всех обработчиков команд и сообщений"""
        # Админские команды
        self.application.add_handler(
            CommandHandler("start", self.admin_handlers.start_command)
        )
        self.application.add_handler(
            CommandHandler("help", self.admin_handlers.help_command)
        )
        self.application.add_handler(
            CommandHandler("add_user", self.admin_handlers.add_user_command)
        )
        self.application.add_handler(
            CommandHandler("remove_user", self.admin_handlers.remove_user_command)
        )
        self.application.add_handler(
            CommandHandler("list_users", self.admin_handlers.list_users_command)
        )
        self.application.add_handler(
            CommandHandler("status", self.admin_handlers.status_command)
        )
        self.application.add_handler(
            CommandHandler("get_user_id", self.admin_handlers.get_user_id_command)
        )
        
        # Обработчик редактированных сообщений
        self.application.add_handler(
            MessageHandler(filters.UpdateType.EDITED_MESSAGE, self.message_handlers.handle_edited_message)
        )
        
        # Обработчик всех сообщений (должен быть последним)
        async def log_all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
            logger.info(f"🔍 ЛЮБОЕ СООБЩЕНИЕ: {update}")
            return await self.message_handlers.handle_message(update, context)
        
        self.application.add_handler(
            MessageHandler(~filters.COMMAND, log_all_messages)
        )
        
        logger.info("✅ Все обработчики зарегистрированы")
    
    async def run(self):
        """Запуск бота"""
        try:
            # Запускаем бота
            await self.application.initialize()
            await self.application.start()
            
            # Получаем информацию о боте
            bot_info = await self.application.bot.get_me()
            logger.info(f"🤖 Бот @{bot_info.username} запущен и готов к работе!")
            
            # Уведомляем администратора о запуске
            try:
                await self.application.bot.send_message(
                    chat_id=self.admin_user_id,
                    text="🤖 *Stenographer Bot запущен\\!*\n\n"
                         "Доступные команды:\n"
                         "• /add\\_user \\- добавить пользователя для отслеживания\n"
                         "• /remove\\_user \\- удалить пользователя из отслеживания\n"
                         "• /list\\_users \\- показать список отслеживаемых пользователей\n"
                         "• /status \\- показать статус бота\n"
                         "• /help \\- справка по командам",
                    parse_mode='MarkdownV2'
                )
            except Exception as e:
                logger.warning(f"⚠️ Не удалось отправить уведомление администратору: {e}")
            
            # Запускаем polling
            await self.application.updater.start_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True
            )
            
            # Ждем остановки
            import signal
            import asyncio
            
            # Создаем event для ожидания сигнала остановки
            stop_event = asyncio.Event()
            
            def signal_handler():
                stop_event.set()
            
            # Устанавливаем обработчики сигналов
            loop = asyncio.get_running_loop()
            for sig in (signal.SIGINT, signal.SIGTERM):
                loop.add_signal_handler(sig, signal_handler)
            
            # Ждем сигнала остановки
            await stop_event.wait()
            
        except Exception as e:
            logger.error(f"❌ Ошибка при запуске бота: {e}")
            raise
        finally:
            await self.application.stop()
            await self.application.shutdown()
    
    async def stop(self):
        """Остановка бота"""
        try:
            await self.application.stop()
            await self.application.shutdown()
            logger.info("✅ Бот остановлен")
        except Exception as e:
            logger.error(f"❌ Ошибка при остановке бота: {e}")
