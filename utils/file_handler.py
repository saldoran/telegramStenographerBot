"""
Утилита для работы с файлами (скачивание голосовых сообщений, медиа и т.д.)
"""

import os
import logging
import asyncio
from datetime import datetime
from pathlib import Path
from telegram import Voice, VideoNote, PhotoSize, Bot
from telegram.error import TelegramError

logger = logging.getLogger(__name__)


class FileHandler:
    """Класс для обработки и сохранения файлов"""
    
    def __init__(self, base_dir: str = "downloads"):
        self.base_dir = Path(base_dir)
        self.voice_dir = self.base_dir / "voice_messages"
        self.video_dir = self.base_dir / "video_notes"
        self.photo_dir = self.base_dir / "photos"
        self.media_dir = self.base_dir / "media"
        
        # Создаем необходимые директории
        self._create_directories()
    
    def _create_directories(self):
        """Создание необходимых директорий для хранения файлов"""
        for directory in [self.voice_dir, self.video_dir, self.photo_dir, self.media_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        logger.info("📁 Директории для файлов созданы")
    
    def _get_timestamp_prefix(self) -> str:
        """Получить временную метку для имени файла"""
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    async def download_voice_message(self, voice: Voice, user_id: int, message_id: int) -> str:
        """Скачивание голосового сообщения"""
        try:
            # Создаем уникальное имя файла
            timestamp = self._get_timestamp_prefix()
            file_name = f"{timestamp}_user{user_id}_msg{message_id}.ogg"
            file_path = self.voice_dir / file_name
            
            # Получаем файл от Telegram
            file = await voice.get_file()
            
            # Скачиваем файл
            await file.download_to_drive(str(file_path))
            
            logger.info(f"🎵 Голосовое сообщение сохранено: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"❌ Ошибка при скачивании голосового сообщения: {e}")
            raise
    
    async def download_video_note(self, video_note: VideoNote, user_id: int, message_id: int) -> str:
        """Скачивание видеосообщения (кружочка)"""
        try:
            timestamp = self._get_timestamp_prefix()
            file_name = f"{timestamp}_user{user_id}_msg{message_id}.mp4"
            file_path = self.video_dir / file_name
            
            file = await video_note.get_file()
            await file.download_to_drive(str(file_path))
            
            logger.info(f"🎥 Видеосообщение сохранено: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"❌ Ошибка при скачивании видеосообщения: {e}")
            raise
    
    async def download_photo(self, photo: PhotoSize, user_id: int, message_id: int) -> str:
        """Скачивание фотографии"""
        try:
            timestamp = self._get_timestamp_prefix()
            file_name = f"{timestamp}_user{user_id}_msg{message_id}.jpg"
            file_path = self.photo_dir / file_name
            
            file = await photo.get_file()
            await file.download_to_drive(str(file_path))
            
            logger.info(f"📸 Фото сохранено: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"❌ Ошибка при скачивании фото: {e}")
            raise
    
    async def download_media_file(self, file_obj, user_id: int, message_id: int, extension: str = "bin") -> str:
        """Общий метод для скачивания медиа файлов"""
        try:
            timestamp = self._get_timestamp_prefix()
            file_name = f"{timestamp}_user{user_id}_msg{message_id}.{extension}"
            file_path = self.media_dir / file_name
            
            file = await file_obj.get_file()
            await file.download_to_drive(str(file_path))
            
            logger.info(f"💾 Медиа файл сохранен: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"❌ Ошибка при скачивании медиа файла: {e}")
            raise
    
    def get_file_info(self, file_path: str) -> dict:
        """Получить информацию о файле"""
        try:
            path = Path(file_path)
            if not path.exists():
                return {"exists": False}
            
            stat = path.stat()
            return {
                "exists": True,
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime),
                "modified": datetime.fromtimestamp(stat.st_mtime),
                "extension": path.suffix,
                "name": path.name
            }
        except Exception as e:
            logger.error(f"❌ Ошибка при получении информации о файле {file_path}: {e}")
            return {"exists": False, "error": str(e)}
    
    def cleanup_old_files(self, days: int = 30):
        """Очистка старых файлов (старше указанного количества дней)"""
        try:
            from datetime import timedelta
            cutoff_date = datetime.now() - timedelta(days=days)
            
            deleted_count = 0
            for directory in [self.voice_dir, self.video_dir, self.photo_dir, self.media_dir]:
                for file_path in directory.iterdir():
                    if file_path.is_file():
                        file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                        if file_time < cutoff_date:
                            try:
                                file_path.unlink()
                                deleted_count += 1
                            except Exception as e:
                                logger.warning(f"⚠️ Не удалось удалить файл {file_path}: {e}")
            
            logger.info(f"🧹 Очищено {deleted_count} старых файлов")
            return deleted_count
            
        except Exception as e:
            logger.error(f"❌ Ошибка при очистке старых файлов: {e}")
            return 0
    
    def get_storage_stats(self) -> dict:
        """Получить статистику использования хранилища"""
        try:
            stats = {
                "voice_files": 0,
                "video_files": 0,
                "photo_files": 0,
                "media_files": 0,
                "total_size": 0
            }
            
            directories = {
                "voice_files": self.voice_dir,
                "video_files": self.video_dir,
                "photo_files": self.photo_dir,
                "media_files": self.media_dir
            }
            
            for key, directory in directories.items():
                if directory.exists():
                    for file_path in directory.iterdir():
                        if file_path.is_file():
                            stats[key] += 1
                            stats["total_size"] += file_path.stat().st_size
            
            # Конвертируем размер в читаемый формат
            stats["total_size_mb"] = round(stats["total_size"] / (1024 * 1024), 2)
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Ошибка при получении статистики хранилища: {e}")
            return {}
