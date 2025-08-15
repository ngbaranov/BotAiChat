import asyncio
import logging
import sys

from os import getenv

from aiogram.types import BotCommand
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher

from app.handlers import select_ai, messages

# Подключение к .env
load_dotenv()
TOKEN = getenv("TOKEN")

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Объект бота
dp = Dispatcher()

dp.include_router(select_ai.router)
dp.include_router(messages.router)

async def set_bot_commands(bot: Bot):
    await bot.set_my_commands([
        BotCommand(command="start", description="Начать настройку"),
        BotCommand(command="model", description="Выбрать/сменить модель"),
        BotCommand(command="provider", description="Сменить провайдера"),
    ])



# Запуск бота
async def main() -> None:
    logger.info("Starting bot...")
    bot = Bot(token=TOKEN)
    await set_bot_commands(bot)
    await dp.start_polling(bot)

#
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user (Ctrl+C)")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
