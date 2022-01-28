import postgres
from aiogram import Bot, Dispatcher, executor, types
import data
from aiogram.contrib.fsm_storage.memory import MemoryStorage

tg_token = data.token

# Initialize bot and dispatcher
bot = Bot(token=tg_token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


import postgres



if __name__ == '__main__':
    from handlers import dp
    executor.start_polling(dp, skip_updates=True)


