import datetime

from aiogram import Bot, Dispatcher, executor
from aiogram.types import ParseMode

import data
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import handlers

tg_token = data.token

storage = MemoryStorage()
bot = Bot(token=tg_token, parse_mode=ParseMode.HTML)
dp = Dispatcher(bot, storage=storage)
from lang_middleware import setup_middleware
i18n = setup_middleware(dp)
_ = i18n.gettext
import postgres
async def on_startup(dispatcher):

    await postgres.startup()
    await set_bot_commands()
    await handlers.kykara4a()
    settings = await postgres.get_settings()
    settings.userbot_id = data.userbot_id
    await settings.update(userbot_id = data.userbot_id).apply()
    now = datetime.datetime.now()
    scheduler = AsyncIOScheduler(timezone="Europe/Kiev")

    scheduler.add_job(handlers.dashboard, 'interval', minutes=1)
    scheduler.add_job(handlers.scan_queue, 'interval', seconds=10)
    scheduler.start()
    print("Bot started")





if __name__ == '__main__':
    from handlers import dp, set_bot_commands

    executor.start_polling(dp, on_startup=on_startup)


