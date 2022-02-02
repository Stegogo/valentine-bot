from aiogram import Bot, Dispatcher, executor
import data

tg_token = data.token

# Initialize bot and dispatcher
bot = Bot(token=tg_token)
dp = Dispatcher(bot)

import postgres
async def on_startup(dispatcher):
    await postgres.startup()


if __name__ == '__main__':
    from handlers import dp
    executor.start_polling(dp, on_startup=on_startup)

