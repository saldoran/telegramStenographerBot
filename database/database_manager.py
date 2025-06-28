"""
Модуль для работы с базой данных SQLite
Содержит функции для создания таблиц и управления данными отслеживаемых пользователей
"""

import sqlite3
import aiosqlite
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
import os

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Класс для управления базой данных SQLite"""
    
    def __init__(self, db_path: str = "stenographer.db"):
        self.db_path = db_path
        
    async def init_database(self):
        """Инициализация базы данных и создание таблиц"""
        async with aiosqlite.connect(self.db_path) as db:
            # Таблица отслеживаемых пользователей
            await db.execute("""
                CREATE TABLE IF NOT EXISTS tracked_users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    added_by INTEGER
                )
            """)
            
            # Таблица сообщений
            await db.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id INTEGER,
                    user_id INTEGER,
                    chat_id INTEGER,
                    message_type TEXT,
                    content TEXT,
                    file_path TEXT,
                    file_id TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_deleted BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (user_id) REFERENCES tracked_users (user_id)
                )
            """)
            
            await db.commit()
            logger.info("✅ База данных инициализирована")
    
    async def add_tracked_user(self, user_id: int, username: str = None, 
                             first_name: str = None, last_name: str = None, 
                             added_by: int = None) -> bool:
        """Добавить пользователя в список отслеживаемых"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO tracked_users 
                    (user_id, username, first_name, last_name, added_by)
                    VALUES (?, ?, ?, ?, ?)
                """, (user_id, username, first_name, last_name, added_by))
                await db.commit()
                logger.info(f"✅ Пользователь {user_id} добавлен в отслеживание")
                return True
        except Exception as e:
            logger.error(f"❌ Ошибка при добавлении пользователя {user_id}: {e}")
            return False
    
    async def remove_tracked_user(self, user_id: int) -> bool:
        """Удалить пользователя из списка отслеживаемых"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(
                    "DELETE FROM tracked_users WHERE user_id = ?", (user_id,)
                )
                await db.commit()
                if cursor.rowcount > 0:
                    logger.info(f"✅ Пользователь {user_id} удален из отслеживания")
                    return True
                else:
                    logger.warning(f"⚠️ Пользователь {user_id} не найден в списке отслеживаемых")
                    return False
        except Exception as e:
            logger.error(f"❌ Ошибка при удалении пользователя {user_id}: {e}")
            return False
    
    async def get_tracked_users(self) -> List[Dict[str, Any]]:
        """Получить список всех отслеживаемых пользователей"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("""
                    SELECT user_id, username, first_name, last_name, added_at 
                    FROM tracked_users ORDER BY added_at DESC
                """) as cursor:
                    rows = await cursor.fetchall()
                    
                users = []
                for row in rows:
                    users.append({
                        'user_id': row[0],
                        'username': row[1],
                        'first_name': row[2],
                        'last_name': row[3],
                        'added_at': row[4]
                    })
                return users
        except Exception as e:
            logger.error(f"❌ Ошибка при получении списка пользователей: {e}")
            return []
    
    async def is_user_tracked(self, user_id: int) -> bool:
        """Проверить, отслеживается ли пользователь"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute(
                    "SELECT 1 FROM tracked_users WHERE user_id = ?", (user_id,)
                ) as cursor:
                    result = await cursor.fetchone()
                    return result is not None
        except Exception as e:
            logger.error(f"❌ Ошибка при проверке пользователя {user_id}: {e}")
            return False
    
    async def save_message(self, message_id: int, user_id: int, chat_id: int,
                          message_type: str, content: str = None, 
                          file_path: str = None, file_id: str = None) -> bool:
        """Сохранить сообщение в базу данных"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO messages 
                    (message_id, user_id, chat_id, message_type, content, file_path, file_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (message_id, user_id, chat_id, message_type, content, file_path, file_id))
                await db.commit()
                logger.info(f"✅ Сообщение {message_id} от пользователя {user_id} сохранено")
                return True
        except Exception as e:
            logger.error(f"❌ Ошибка при сохранении сообщения: {e}")
            return False
    
    async def mark_message_deleted(self, message_id: int, user_id: int, chat_id: int) -> bool:
        """Отметить сообщение как удаленное"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    UPDATE messages 
                    SET is_deleted = TRUE 
                    WHERE message_id = ? AND user_id = ? AND chat_id = ?
                """, (message_id, user_id, chat_id))
                await db.commit()
                if cursor.rowcount > 0:
                    logger.info(f"✅ Сообщение {message_id} отмечено как удаленное")
                    return True
                return False
        except Exception as e:
            logger.error(f"❌ Ошибка при отметке сообщения как удаленного: {e}")
            return False
    
    async def get_user_messages(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Получить последние сообщения от пользователя"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("""
                    SELECT message_id, user_id, chat_id, message_type, content, 
                           file_path, timestamp, is_deleted 
                    FROM messages 
                    WHERE user_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (user_id, limit)) as cursor:
                    rows = await cursor.fetchall()
                    
                messages = []
                for row in rows:
                    messages.append({
                        'message_id': row[0],
                        'user_id': row[1],
                        'chat_id': row[2],
                        'message_type': row[3],
                        'content': row[4],
                        'file_path': row[5],
                        'timestamp': row[6],
                        'is_deleted': row[7]
                    })
                return messages
        except Exception as e:
            logger.error(f"❌ Ошибка при получении сообщений пользователя {user_id}: {e}")
            return []

    async def close(self):
        """Закрыть соединение с базой данных"""
        logger.info("📊 Соединение с базой данных закрыто")
