"""
Обработчики административных команд бота
"""

import logging
from typing import List, Dict, Any
from telegram import Update
from telegram.ext import ContextTypes
from database.database_manager import DatabaseManager

logger = logging.getLogger(__name__)


class AdminHandlers:
    """Класс для обработки административных команд"""
    
    def __init__(self, db_manager: DatabaseManager, admin_user_id: int):
        self.db_manager = db_manager
        self.admin_user_id = admin_user_id

    def _is_admin(self, user_id: int) -> bool:
        """Проверяет, является ли пользователь администратором"""
        return user_id == self.admin_user_id

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        logger.info(f"🔧 КОМАНДА /start от пользователя {update.effective_user.id}")
        welcome_text = (
            "🤖 *Добро пожаловать в Telegram Stenographer Bot\\!*\n\n"
            "Этот бот поможет вам отслеживать сообщения от указанных пользователей\\.\n\n"
            "*Доступные команды:*\n"
            "• `/add_user <user_id>` \\- добавить пользователя для отслеживания\n"
            "• `/remove_user <user_id>` \\- удалить пользователя из отслеживания\n"
            "• `/list_users` \\- показать список отслеживаемых пользователей\n"
            "• `/get_user_id` \\- узнать User ID пользователя\n"
            "• `/status` \\- показать статус бота\n"
            "• `/help` \\- справка по командам\n\n"
            "📝 *Как получить user\\_id:*\n"
            "1\\. Ответьте командой `/get_user_id` на сообщение пользователя\n"
            "2\\. Или используйте бота @userinfobot\n"
            "3\\. Добавьте бота в чат и используйте `/get_user_id`"
        )
        
        await update.message.reply_text(welcome_text, parse_mode='MarkdownV2')

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        help_text = (
            "🤖 *Telegram Stenographer Bot \\- Справка*\n\n"
            "*Основные команды:*\n"
            "• `/start` \\- приветствие и краткая информация\n"
            "• `/help` \\- показать эту справку\n"
            "• `/status` \\- показать статус бота и статистику\n\n"
            "*Управление пользователями:*\n"
            "• `/add_user <user_id>` \\- добавить пользователя в отслеживание\n"
            "  Пример: `/add_user 123456789`\n"
            "• `/remove_user <user_id>` \\- удалить пользователя из отслеживания\n"
            "  Пример: `/remove_user 123456789`\n"
            "• `/list_users` \\- показать всех отслеживаемых пользователей\n"
            "• `/get_user_id` \\- узнать User ID \\(ответом на сообщение\\)\n\n"
            "*Функции бота:*\n"
            "🔍 Отслеживает все сообщения от указанных пользователей\n"
            "📤 Сразу дублирует сообщения в тот же чат\n"
            "✏️ Уведомляет об отредактированных сообщениях\n"
            "📊 Показывает информацию об отправителе"
        )
        
        await update.message.reply_text(help_text, parse_mode='MarkdownV2')
    
    async def add_user_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /add_user"""
        if not self._is_admin(update.effective_user.id):
            await update.message.reply_text("❌ У вас нет прав для выполнения этой команды.")
            return
        
        if not context.args:
            await update.message.reply_text(
                "❌ Укажите ID пользователя\\.\n"
                "Пример: `/add_user 123456789`",
                parse_mode='MarkdownV2'
            )
            return
        
        try:
            user_id = int(context.args[0])
        except ValueError:
            await update.message.reply_text("❌ ID пользователя должен быть числом.")
            return
        
        # Проверяем, не отслеживается ли уже пользователь
        if await self.db_manager.is_user_tracked(user_id):
            await update.message.reply_text(f"⚠️ Пользователь с ID `{user_id}` уже отслеживается\\.", parse_mode='MarkdownV2')
            return
        
        # Добавляем пользователя
        success = await self.db_manager.add_tracked_user(user_id)
        
        if success:
            await update.message.reply_text(f"✅ Пользователь с ID `{user_id}` добавлен в отслеживание\\.", parse_mode='MarkdownV2')
            logger.info(f"Admin {update.effective_user.id} added user {user_id} to tracking")
        else:
            await update.message.reply_text("❌ Произошла ошибка при добавлении пользователя.")

    async def remove_user_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /remove_user"""
        if not self._is_admin(update.effective_user.id):
            await update.message.reply_text("❌ У вас нет прав для выполнения этой команды.")
            return
        
        if not context.args:
            await update.message.reply_text(
                "❌ Укажите ID пользователя\\.\n"
                "Пример: `/remove_user 123456789`",
                parse_mode='MarkdownV2'
            )
            return
        
        try:
            user_id = int(context.args[0])
        except ValueError:
            await update.message.reply_text("❌ ID пользователя должен быть числом.")
            return
        
        # Проверяем, отслеживается ли пользователь
        if not await self.db_manager.is_user_tracked(user_id):
            await update.message.reply_text(f"⚠️ Пользователь с ID `{user_id}` не отслеживается\\.", parse_mode='MarkdownV2')
            return
        
        # Удаляем пользователя
        success = await self.db_manager.remove_tracked_user(user_id)
        
        if success:
            await update.message.reply_text(f"✅ Пользователь с ID `{user_id}` удален из отслеживания\\.", parse_mode='MarkdownV2')
            logger.info(f"Admin {update.effective_user.id} removed user {user_id} from tracking")
        else:
            await update.message.reply_text("❌ Произошла ошибка при удалении пользователя.")

    async def list_users_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /list_users"""
        if not self._is_admin(update.effective_user.id):
            await update.message.reply_text("❌ У вас нет прав для выполнения этой команды.")
            return
        
        tracked_users = await self.db_manager.get_tracked_users()
        
        if not tracked_users:
            await update.message.reply_text("📭 Нет отслеживаемых пользователей\\.", parse_mode='MarkdownV2')
            return
        
        message = "👥 *Отслеживаемые пользователи:*\n\n"
        for i, user_data in enumerate(tracked_users, 1):
            user_id = user_data.get('user_id')
            username = user_data.get('username', 'Неизвестно')
            first_name = user_data.get('first_name', 'Неизвестно')
            last_name = user_data.get('last_name', '')
            
            # Экранируем специальные символы для MarkdownV2
            if username and username != 'Неизвестно':
                username = username.replace("_", "\\_").replace("*", "\\*").replace("[", "\\[").replace("]", "\\]").replace("(", "\\(").replace(")", "\\)").replace("~", "\\~").replace("`", "\\`").replace(">", "\\>").replace("#", "\\#").replace("+", "\\+").replace("-", "\\-").replace("=", "\\=").replace("|", "\\|").replace("{", "\\{").replace("}", "\\}").replace(".", "\\.").replace("!", "\\!")
            
            if first_name and first_name != 'Неизвестно':
                first_name = first_name.replace("_", "\\_").replace("*", "\\*").replace("[", "\\[").replace("]", "\\]").replace("(", "\\(").replace(")", "\\)").replace("~", "\\~").replace("`", "\\`").replace(">", "\\>").replace("#", "\\#").replace("+", "\\+").replace("-", "\\-").replace("=", "\\=").replace("|", "\\|").replace("{", "\\{").replace("}", "\\}").replace(".", "\\.").replace("!", "\\!")
            
            if last_name:
                last_name = last_name.replace("_", "\\_").replace("*", "\\*").replace("[", "\\[").replace("]", "\\]").replace("(", "\\(").replace(")", "\\)").replace("~", "\\~").replace("`", "\\`").replace(">", "\\>").replace("#", "\\#").replace("+", "\\+").replace("-", "\\-").replace("=", "\\=").replace("|", "\\|").replace("{", "\\{").replace("}", "\\}").replace(".", "\\.").replace("!", "\\!")
            
            full_name = f"{first_name} {last_name}".strip() if last_name else first_name
            
            message += f"{i}\\. *ID:* `{user_id}`\n"
            if username and username != 'Неизвестно':
                message += f"   *Username:* @{username}\n"
            message += f"   *Имя:* {full_name}\n\n"
        
        await update.message.reply_text(message, parse_mode='MarkdownV2')

    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /status"""
        if not self._is_admin(update.effective_user.id):
            await update.message.reply_text("❌ У вас нет прав для выполнения этой команды.")
            return
        
        try:
            # Получаем статистику
            tracked_users_count = len(await self.db_manager.get_tracked_users())
            
            status_text = (
                "📊 *Статус Telegram Stenographer Bot*\n\n"
                f"🟢 *Статус:* Работает\n"
                f"👥 *Отслеживаемых пользователей:* {tracked_users_count}\n"
                f"🤖 *Режим работы:* Дублирование сообщений\n\n"
                f"🆔 *ID Администратора:* `{self.admin_user_id}`\n"
                f"👤 *Ваш ID:* `{update.effective_user.id}`"
            )
            
        except Exception as e:
            status_text = (
                "📊 *Статус Telegram Stenographer Bot*\n\n"
                f"🔴 *Статус:* Ошибка при получении статистики\n"
                f"❌ *Ошибка:* {str(e)}"
            )
        
        await update.message.reply_text(status_text, parse_mode='MarkdownV2')

    async def get_user_id_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /get_user_id"""
        # Эта команда доступна всем пользователям
        
        if update.message.reply_to_message:
            # Если команда является ответом на сообщение
            user = update.message.reply_to_message.from_user
            user_info = (
                f"🆔 *Информация о пользователе:*\n\n"
                f"*User ID:* `{user.id}`\n"
                f"*Имя:* {user.first_name or 'Не указано'}\n"
                f"*Фамилия:* {user.last_name or 'Не указана'}\n"
                f"*Username:* @{user.username or 'не указан'}\n"
                f"*Тип:* {'Бот' if user.is_bot else 'Пользователь'}"
            )
            
            await update.message.reply_text(user_info, parse_mode='MarkdownV2')
        else:
            # Показываем информацию о том, как получить User ID
            admin_info = (
                "🆔 *Как узнать User ID пользователя?*\n\n"
                "*Способ 1 \\- через этого бота:*\n"
                "• Ответьте командой `/get_user_id` на сообщение пользователя\n"
                "• Бот покажет полную информацию о пользователе\n\n"
                "*Способ 2 \\- через специальных ботов:*\n"
                "• @userinfobot \\- перешлите сообщение пользователя\n"
                "• @get\\_id\\_bot \\- отправьте команду `/start`\n"
                "• @username\\_to\\_id\\_bot \\- введите username\n\n"
                "*Способ 3 \\- в группе/чате:*\n"
                "• Добавьте этого бота в чат\n"
                "• Используйте `/get_user_id` ответом на сообщения\n\n"
                f"🆔 *Ваш User ID:* `{update.effective_user.id}`\n"
                f"👤 *Ваш Username:* @{update.effective_user.username or 'не указан'}"
            )
            
            await update.message.reply_text(admin_info, parse_mode='MarkdownV2')
