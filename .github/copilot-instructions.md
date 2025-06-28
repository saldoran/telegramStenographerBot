<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Telegram Stenographer Bot Project Instructions

This is a Python Telegram bot project that acts as a stenographer, tracking and storing messages from specified users.

## Key Features:
- Track messages from specific users (including deleted messages)
- Store all message types: text, voice, media, stickers, etc.
- Admin commands to manage tracked users
- SQLite database for data persistence
- Voice message handling and storage

## Architecture:
- `main.py` - Entry point and bot initialization
- `bot/` - Core bot functionality
- `database/` - Database models and operations
- `handlers/` - Message and command handlers
- `utils/` - Utility functions

## Development Guidelines:
- Use python-telegram-bot library
- Follow async/await patterns
- Implement proper error handling
- Use type hints for better code quality
- Store sensitive data in environment variables
