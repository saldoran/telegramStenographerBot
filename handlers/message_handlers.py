"""
Обработчики сообщений от отслеживаемых пользователей
"""

import logging
import os
from datetime import datetime
from telegram import Update, Message
from telegram.ext import ContextTypes
from database.database_manager import DatabaseManager
from utils.file_handler import FileHandler

logger = logging.getLogger(__name__)


class MessageHandlers:
    """Класс для обработки сообщений от отслеживаемых пользователей"""
    
    def __init__(self, db_manager: DatabaseManager, file_handler: FileHandler):
        self.db_manager = db_manager
        self.file_handler = file_handler
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Основной обработчик всех сообщений"""
        logger.info(f"🔍 ПОЛУЧЕНО ОБНОВЛЕНИЕ: update.message={update.message is not None}, "
                   f"update.edited_message={update.edited_message is not None}")
        
        # Обрабатываем обычные сообщения
        if update.message and update.message.from_user:
            message = update.message
            user_id = message.from_user.id
            username = message.from_user.username or "без_username"
            
            logger.info(f"🔍 СООБЩЕНИЕ ОТ ПОЛЬЗОВАТЕЛЯ: ID={user_id}, username={username}, chat_id={message.chat_id}")
            
            # Проверяем, отслеживается ли пользователь
            is_tracked = await self.db_manager.is_user_tracked(user_id)
            logger.info(f"🔍 ПРОВЕРКА ОТСЛЕЖИВАНИЯ: пользователь {user_id} отслеживается: {is_tracked}")
            
            if is_tracked:
                logger.info(f"✅ ЗАПУСКАЕМ ДУБЛИРОВАНИЕ для пользователя {user_id}")
                await self._process_message(message)
            else:
                logger.info(f"ℹ️ ПРОПУСКАЕМ: пользователь {user_id} не отслеживается")
        else:
            logger.info(f"ℹ️ ПРОПУСКАЕМ: нет message или from_user")
        
        # Обрабатываем редактированные сообщения
        if update.edited_message and update.edited_message.from_user:
            await self.handle_edited_message(update, context)
    
    async def _process_message(self, message: Message):
        """Обработка и дублирование сообщения в чат"""
        user_id = message.from_user.id
        chat_id = message.chat_id
        message_id = message.message_id
        
        logger.info(f"🔄 Начинаем дублирование сообщения {message_id} от пользователя {user_id} в чате {chat_id}")
        
        # Получаем информацию о пользователе
        username = message.from_user.username or "без_username"
        first_name = message.from_user.first_name or ""
        last_name = message.from_user.last_name or ""
        full_name = f"{first_name} {last_name}".strip() or "Без имени"
        
        # Определяем отображаемое имя
        display_name = f"@{username}" if username != "без_username" else full_name
        
        # Определяем тип сообщения и отправляем дубликат
        try:
            if message.text:
                # Текстовое сообщение
                duplicate_text = f"💬 {display_name}: {message.text}"
                await message.get_bot().send_message(
                    chat_id=chat_id,
                    text=duplicate_text,
                    reply_to_message_id=message_id
                )
                
            elif message.voice:
                # Голосовое сообщение
                duration = message.voice.duration
                duplicate_text = f"🎵 {display_name}: Голосовое сообщение ({duration}с)"
                await message.get_bot().send_message(
                    chat_id=chat_id,
                    text=duplicate_text,
                    reply_to_message_id=message_id
                )
                
            elif message.video_note:
                # Видеосообщение (кружочек)
                duration = message.video_note.duration
                duplicate_text = f"🎥 {display_name}: Видеосообщение ({duration}с)"
                await message.get_bot().send_message(
                    chat_id=chat_id,
                    text=duplicate_text,
                    reply_to_message_id=message_id
                )
                
            elif message.photo:
                # Фото
                caption = message.caption or ""
                if caption:
                    duplicate_text = f"📷 {display_name}: {caption}"
                else:
                    duplicate_text = f"📸 {display_name}: Фото"
                await message.get_bot().send_message(
                    chat_id=chat_id,
                    text=duplicate_text,
                    reply_to_message_id=message_id
                )
                
            elif message.sticker:
                # Стикер
                emoji = message.sticker.emoji or "❓"
                duplicate_text = f"🎭 {display_name}: Стикер {emoji}"
                await message.get_bot().send_message(
                    chat_id=chat_id,
                    text=duplicate_text,
                    reply_to_message_id=message_id
                )
                
            elif message.document:
                # Документ
                file_name = message.document.file_name or "Документ"
                caption = message.caption or ""
                if caption:
                    duplicate_text = f"📄 {display_name}: {caption}"
                else:
                    duplicate_text = f"📄 {display_name}: {file_name}"
                await message.get_bot().send_message(
                    chat_id=chat_id,
                    text=duplicate_text,
                    reply_to_message_id=message_id
                )
                
            else:
                # Другие типы сообщений
                duplicate_text = f"❓ {display_name}: Сообщение"
                await message.get_bot().send_message(
                    chat_id=chat_id,
                    text=duplicate_text,
                    reply_to_message_id=message_id
                )
            
            logger.info(f"✅ Успешно продублировано сообщение от @{username} ({full_name}, ID: {user_id}) в чате {chat_id}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка при дублировании сообщения от {user_id}: {e}")
            # В случае ошибки, попробуем отправить без reply_to
            try:
                error_text = f"❌ {display_name}: Не удалось продублировать сообщение"
                await message.get_bot().send_message(chat_id=chat_id, text=error_text)
            except Exception as e2:
                logger.error(f"❌ Критическая ошибка при отправке дубликата: {e2}")
    
    async def _analyze_message(self, message: Message) -> tuple:
        """Анализ сообщения и определение его типа"""
        content = None
        file_path = None
        file_id = None
        
        if message.text:
            message_type = "text"
            content = message.text
            
        elif message.voice:
            message_type = "voice"
            file_id = message.voice.file_id
            content = f"Голосовое сообщение (длительность: {message.voice.duration}с)"
            
            # Скачиваем голосовое сообщение
            try:
                file_path = await self.file_handler.download_voice_message(
                    message.voice, message.from_user.id, message.message_id
                )
            except Exception as e:
                logger.error(f"❌ Ошибка при скачивании голосового сообщения: {e}")
                
        elif message.video_note:
            message_type = "video_note"
            file_id = message.video_note.file_id
            content = f"Видеосообщение (длительность: {message.video_note.duration}с)"
            
            try:
                file_path = await self.file_handler.download_video_note(
                    message.video_note, message.from_user.id, message.message_id
                )
            except Exception as e:
                logger.error(f"❌ Ошибка при скачивании видеосообщения: {e}")
                
        elif message.photo:
            message_type = "photo"
            file_id = message.photo[-1].file_id  # Берем фото наибольшего размера
            content = "Фото"
            if message.caption:
                content += f" с подписью: {message.caption}"
                
            try:
                file_path = await self.file_handler.download_photo(
                    message.photo[-1], message.from_user.id, message.message_id
                )
            except Exception as e:
                logger.error(f"❌ Ошибка при скачивании фото: {e}")
                
        elif message.video:
            message_type = "video"
            file_id = message.video.file_id
            content = f"Видео (длительность: {message.video.duration}с)"
            if message.caption:
                content += f" с подписью: {message.caption}"
                
        elif message.document:
            message_type = "document"
            file_id = message.document.file_id
            content = f"Документ: {message.document.file_name}"
            if message.caption:
                content += f" с подписью: {message.caption}"
                
        elif message.audio:
            message_type = "audio"
            file_id = message.audio.file_id
            content = f"Аудио (длительность: {message.audio.duration}с)"
            if message.audio.title:
                content += f" - {message.audio.title}"
            if message.caption:
                content += f" с подписью: {message.caption}"
                
        elif message.sticker:
            message_type = "sticker"
            file_id = message.sticker.file_id
            content = f"Стикер: {message.sticker.emoji or '❓'}"
            if message.sticker.set_name:
                content += f" из набора {message.sticker.set_name}"
                
        elif message.animation:
            message_type = "gif"
            file_id = message.animation.file_id
            content = "GIF анимация"
            if message.caption:
                content += f" с подписью: {message.caption}"
                
        elif message.location:
            message_type = "location"
            content = f"Местоположение: {message.location.latitude}, {message.location.longitude}"
            
        elif message.contact:
            message_type = "contact"
            content = f"Контакт: {message.contact.first_name}"
            if message.contact.last_name:
                content += f" {message.contact.last_name}"
            if message.contact.phone_number:
                content += f", тел: {message.contact.phone_number}"
                
        elif message.poll:
            message_type = "poll"
            content = f"Опрос: {message.poll.question}"
            
        else:
            message_type = "other"
            content = "Неизвестный тип сообщения"
        
        return message_type, content, file_path, file_id
    
    async def handle_edited_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик отредактированных сообщений"""
        edited_message = update.edited_message
        if not edited_message or not edited_message.from_user:
            return
        
        user_id = edited_message.from_user.id
        chat_id = edited_message.chat_id
        
        logger.info(f"✏️ Получено отредактированное сообщение от пользователя {user_id}")
        
        # Проверяем, отслеживается ли пользователь
        is_tracked = await self.db_manager.is_user_tracked(user_id)
        if not is_tracked:
            logger.info(f"ℹ️ Пользователь {user_id} не отслеживается, пропускаем редактированное сообщение")
            return
        
        # Получаем информацию о пользователе
        username = edited_message.from_user.username or "без_username"
        first_name = edited_message.from_user.first_name or ""
        last_name = edited_message.from_user.last_name or ""
        full_name = f"{first_name} {last_name}".strip() or "Без имени"
        
        # Формируем заголовок
        user_info = f"👤 {full_name}"
        if username != "без_username":
            user_info += f" (@{username})"
        user_info += f" | ID: {user_id}"
        
        # Сообщение о редактировании
        try:
            if edited_message.text:
                duplicate_text = f"✏️ **СТЕНОГРАФ - ОТРЕДАКТИРОВАНО**\n{user_info}\n\n📝 Новый текст:\n{edited_message.text}"
            else:
                duplicate_text = f"✏️ **СТЕНОГРАФ - ОТРЕДАКТИРОВАНО**\n{user_info}\n\n❓ Отредактированное сообщение"
            
            await edited_message.get_bot().send_message(
                chat_id=chat_id,
                text=duplicate_text,
                reply_to_message_id=edited_message.message_id
            )
            
            logger.info(f"✅ Успешно обработано отредактированное сообщение от пользователя {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка при отправке уведомления о редактировании: {e}")
            # Попробуем отправить без reply_to
            try:
                error_text = f"✏️ **СТЕНОГРАФ - ОТРЕДАКТИРОВАНО** (ошибка reply)\n{user_info}\n\n❌ Не удалось показать детали"
                await edited_message.get_bot().send_message(chat_id=chat_id, text=error_text)
            except Exception as e2:
                logger.error(f"❌ Критическая ошибка при отправке уведомления о редактировании: {e2}")
