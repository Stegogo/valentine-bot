import postgres
from aiogram import Bot, Dispatcher, executor, types
import data

tg_token = data.token

# Initialize bot and dispatcher
bot = Bot(token=tg_token)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Hi!\nI'm EchoBot!\nPowered by aiogram.")
    await postgres.main()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)


