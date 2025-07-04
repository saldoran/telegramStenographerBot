# 🚀 Быстрая настройка Telegram Stenographer Bot

## Шаг 1: Создание бота в Telegram

1. Откройте [@BotFather](https://t.me/BotFather) в Telegram
2. Отправьте команду `/newbot`
3. Введите имя бота (например: "My Stenographer Bot")
4. Введите username бота (например: "my_stenographer_bot")
5. Скопируйте полученный токен

## Шаг 2: Получение вашего User ID

### Способ 1 - через @userinfobot:
1. Откройте [@userinfobot](https://t.me/userinfobot)
2. Отправьте любое сообщение боту
3. Скопируйте ваш User ID из ответа

### Способ 2 - через @get_id_bot:
1. Откройте [@get_id_bot](https://t.me/get_id_bot)
2. Отправьте команду `/start`
3. Скопируйте ваш User ID

## Шаг 3: Настройка проекта

1. **Скопируйте файл конфигурации:**
   ```bash
   cp .env.example .env
   ```

2. **Откройте файл `.env` и заполните переменные:**
   ```env
   BOT_TOKEN=ваш_токен_от_BotFather
   ADMIN_USER_ID=ваш_telegram_user_id
   ```

3. **Проверьте конфигурацию:**
   ```bash
   python tools.py config
   ```

## Шаг 4: Запуск бота

### Вариант 1 - через скрипт:
```bash
./run_bot.sh
```

### Вариант 2 - напрямую:
```bash
source venv/bin/activate
python main.py
```

### Вариант 3 - через Makefile:
```bash
make run
```

## Шаг 5: Тестирование

1. Найдите вашего бота в Telegram по username
2. Отправьте команду `/start`
3. Добавьте пользователя для отслеживания: `/add_user USER_ID`
4. Проверьте список: `/list_users`

## 🔧 Полезные команды

- `python tools.py stats` - статистика бота
- `python tools.py config` - проверка настроек
- `make clean` - очистка временных файлов
- `make test` - проверка синтаксиса

## ⚠️ Важно!

- Добавьте бота в чаты, где нужно отслеживать сообщения
- Дайте боту права администратора для доступа ко всем сообщениям
- Регулярно проверяйте место на диске (голосовые сообщения занимают место)

## 🆘 Возможные проблемы

### Бот не отвечает:
- Проверьте токен в `.env`
- Убедитесь, что бот запущен
- Проверьте логи в терминале

### Не сохраняются сообщения:
- Убедитесь, что пользователь добавлен в отслеживание
- Проверьте права бота в чате
- Проверьте логи базы данных

### Ошибки при скачивании файлов:
- Проверьте права на запись в папку `downloads/`
- Убедитесь, что достаточно места на диске
