import os
import asyncio

from dotenv import load_dotenv
from aiogram import Dispatcher, Bot
from app.handlers import router

from app.database.core import get_tasks

load_dotenv(override=True)

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)


dp = Dispatcher()


async def main():
    tasks = await get_tasks()
    bot.tasks = {task.get("id"): task for task in tasks}
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())