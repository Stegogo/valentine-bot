import postgres
from aiogram import Bot, Dispatcher, executor, types
import data

tg_token = data.token

# Initialize bot and dispatcher
bot = Bot(token=tg_token)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    users = await postgres.main()

    if message.from_user.id in users:
        #Кидаем здесь нужный стейт
        print("Вы есть в базе данных")
    else:
        await message.answer("Привет! Я бот, который отправляет поздравления другим людям!")
        print("Вас нет в базе данных")
        await postgres.create(message.from_user.id)



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)


