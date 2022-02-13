import datetime

from aiogram import Bot, Dispatcher, executor
import data
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import handlers

tg_token = data.token

storage = MemoryStorage()
bot = Bot(token=tg_token)
dp = Dispatcher(bot, storage=storage)

import postgres
async def on_startup(dispatcher):
    await postgres.startup()
    await set_bot_commands()
    now = datetime.datetime.now()
    scheduler = AsyncIOScheduler(timezone="Europe/Kiev")

    scheduler.add_job(handlers.dashboard, 'interval', minutes=1)
    scheduler.add_job(handlers.scan_queue, 'interval', seconds=20)
    scheduler.start()
    print("Bot started")


if __name__ == '__main__':
    from handlers import dp, set_bot_commands

    executor.start_polling(dp, on_startup=on_startup)


