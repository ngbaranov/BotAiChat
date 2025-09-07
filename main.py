import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.types import (
    BotCommand,
    BotCommandScopeDefault,
    BotCommandScopeAllPrivateChats,
    BotCommandScopeAllGroupChats,
)
from dotenv import load_dotenv

# ── Handlers
from app.handlers import select_ai, messages

# (опционально) подключим messages_txt, если модуль существует
try:
    from app.handlers import messages_txt
    HAS_MESSAGES_TXT = True
except Exception:
    HAS_MESSAGES_TXT = False

# ── ENV / TOKEN
load_dotenv()
TOKEN = getenv("TOKEN")

# ── Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# ── Bot & Dispatcher
dp = Dispatcher()
dp.include_router(select_ai.router)
dp.include_router(messages.router)
if HAS_MESSAGES_TXT:
    dp.include_router(messages_txt.router)


async def set_bot_commands(bot: Bot) -> None:
    """Полный сброс и установка команд во всех скоупах."""
    commands = [
        BotCommand(command="start", description="Начать настройку"),
        BotCommand(command="model", description="Выбрать/сменить модель"),
        BotCommand(command="provider", description="Сменить провайдера"),
        BotCommand(command="clear", description="Вернуться в чат с ИИ"),
        BotCommand(command="info", description="Показать текущего провайдера и модель"),
    ]

    # Сбросим возможные старые списки (чтобы не перекрывали новый)
    await bot.set_my_commands([], scope=BotCommandScopeAllPrivateChats())
    await bot.set_my_commands([], scope=BotCommandScopeAllGroupChats())
    await bot.set_my_commands([], scope=BotCommandScopeDefault())

    # Поставим единый набор в каждый скоуп
    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())
    await bot.set_my_commands(commands, scope=BotCommandScopeAllPrivateChats())
    await bot.set_my_commands(commands, scope=BotCommandScopeAllGroupChats())


async def main() -> None:
    if not TOKEN:
        logger.error("TOKEN не найден в .env")
        return

    logger.info("Starting bot…")
    bot = Bot(token=TOKEN)

    # Важно: сначала команды, потом polling
    await set_bot_commands(bot)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user (Ctrl+C)")
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
