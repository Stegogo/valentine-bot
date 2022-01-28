from aiogram.dispatcher import FSMContext
import Letter_class
from main import bot, dp
from keyboard import keyboard
from aiogram import types

from aiogram.dispatcher.filters import Command


@dp.message_handler(Command('love'), state=None)
async def enter_username(message: types.Message):
    await message.answer('Отправь нам @юзернейм твоей радости🥰')
    await Letter_class.Letter.q_username.set()


@dp.message_handler(state=Letter_class.Letter.q_username)
async def username_answer(message: types.Message, state: FSMContext):
    username = message.text
    await state.update_data(answer1=username)
    await message.answer('Супер! Мы нашли его! Теперь мы ждём текст твоей валентинки🧐')
    await Letter_class.Letter.q_text_val.set()

@dp.message_handler(state=Letter_class.Letter.q_text_val)
async def text_val_answer(message: types.Message, state: FSMContext):
    data = await state.get_data()
    username = data.get('answer1')
    text_val = message.text
    await message.answer('Я всё правильно понял?')
    await message.answer(f'Твоя валентинка будет отправлена пользователю {username}')
    await message.answer('Текст валентинки: ')
    await message.answer(text_val, reply_markup=keyboard)
    await state.finish()

@dp.callback_query_handler(lambda c: c.data == 'good')
async def process_callback_button1(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Мы всё записали) Хорошего дня!')



@dp.callback_query_handler(lambda c: c.data == 'bad')
async def process_callback_button1(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Отправь нам @юзернейм твоей радости🥰')
    await Letter_class.Letter.q_username.set()