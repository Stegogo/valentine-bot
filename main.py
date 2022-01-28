import postgres
from aiogram import Bot, Dispatcher, executor, types
import data
from aiogram.contrib.fsm_storage.memory import MemoryStorage

tg_token = data.token

# Initialize bot and dispatcher
bot = Bot(token=tg_token)
dp = Dispatcher(bot)
storage = MemoryStorage()





if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)


