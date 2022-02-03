from aiogram import Bot, Dispatcher, executor
import data
from aiogram.contrib.fsm_storage.memory import MemoryStorage

tg_token = data.token

storage = MemoryStorage()
bot = Bot(token=tg_token)
dp = Dispatcher(bot, storage=storage)

import postgres
async def on_startup(dispatcher):
    await postgres.startup()


if __name__ == '__main__':
    from handlers import dp
    executor.start_polling(dp, on_startup=on_startup)

