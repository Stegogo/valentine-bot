from aiogram.dispatcher import FSMContext
import states
from data import moder_chat_id
from main import bot, dp
from keyboard import menu_cd, is_correct_keyboard
from aiogram import types
import postgres
import models

from aiogram.dispatcher.filters import Command


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    users = await postgres.get_users(1)

    if message.from_user.id in users:
        await message.answer('Отправь нам @юзернейм твоей радости🥰')
        await states.Letter.q_username.set()
    else:
        # Срабатывает, если пользователя нет в дб и добавляет его туда
        await message.answer("Привет! Я бот, который отправляет поздравления другим людям!")
        await postgres.create_user(message.from_user.id)  #
        await message.answer('Отправь нам @юзернейм твоей радости🥰')
        await states.Letter.q_username.set()


@dp.message_handler(state=states.Letter.q_username)
async def username_answer(message: types.Message, state: FSMContext):

    username = message.text
    if username.startswith('@') or username.startswith('+'):
        await state.update_data(answer1=username)
        await message.answer('Супер! Мы нашли его! Теперь мы ждём текст твоей валентинки🧐')
        await states.Letter.q_text_val.set()
    else:
        await message.answer('Введи коректный юзернейм. Начни с @')


@dp.message_handler(state=states.Letter.q_text_val)
async def text_val_answer(message: types.Message, state: FSMContext):

    data = await state.get_data()
    username = data.get('answer1')
    text_val = message.text
    await state.update_data(answer2=text_val)

    letter = models.Letter()

    letter.recipient_username = username
    letter.text = text_val
    letter.sender_id = message.from_user.id

    letter = await letter.create()

    await state.update_data(letter_id=letter.id)

    await message.answer('Я всё правильно понял?')
    await message.answer(f'Твоя валентинка будет отправлена пользователю {username}')
    await message.answer('Текст валентинки: ')
    keyboard = await is_correct_keyboard(letter)
    await message.answer(text_val, reply_markup=keyboard)


@dp.message_handler(state=states.Letter.correct_username)
async def text_val_answer1(message: types.Message, state: FSMContext):

    data = await state.get_data()
    username = message.text
    text_val = data.get('answer2')
    letter_id = data.get("letter_id")

    await message.answer('Я всё правильно понял?')
    await message.answer(f'Твоя валентинка будет отправлена пользователю {username}')
    await message.answer('Текст валентинки: ')

    letter = await models.Letter.get(letter_id)

    letter.recipient_username = username
    letter.text = text_val
    letter.sender_id = message.from_user.id

    await letter.update(recipient_username=username).apply()

    keyboard = await is_correct_keyboard(letter)
    await message.answer(text_val, reply_markup=keyboard)


@dp.message_handler(state=states.Letter.correct_val)
async def text_val_answer(message: types.Message, state: FSMContext):

    data = await state.get_data()
    username = data.get('answer1')
    text_val = message.text
    letter_id = data.get("letter_id")

    await state.update_data(answer2=text_val)
    await message.answer('Я всё правильно понял?')
    await message.answer(f'Твоя валентинка будет отправлена пользователю {username}')
    await message.answer('Текст валентинки: ')

    letter = await models.Letter.get(letter_id)

    letter.recipient_username = username
    letter.text = text_val
    letter.sender_id = message.from_user.id

    await letter.update(text=text_val).apply()


    keyboard = await is_correct_keyboard(letter)
    await message.answer(text_val, reply_markup=keyboard)


async def process_callback_button1(callback_query: types.CallbackQuery, **kwargs):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Отправь исправленный юзернейм')
    await states.Letter.correct_username.set()


async def process_callback_button2(callback_query: types.CallbackQuery, **kwargs):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Отправь новую валентинку')
    await states.Letter.correct_val.set()


@dp.message_handler(state=states.Letter.send_to_moder)
async def process_callback_button3(callback_query: types.CallbackQuery, id, **kwargs):


    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Отправили!')
    letter = await postgres.get_letter(int(id))
    await bot.send_message(moder_chat_id, 'Юзернейм')
    await bot.send_message(moder_chat_id, letter.recipient_username)
    await bot.send_message(moder_chat_id, 'Текст валентинки')
    await bot.send_message(moder_chat_id, letter.text)


@dp.callback_query_handler(menu_cd.filter(), state='*')
async def navigate(call: types.CallbackQuery, callback_data: dict):
    current_level = callback_data.get('level')
    id = callback_data.get('id')

    levels = {
        '1': process_callback_button1,
        '2': process_callback_button2,
        '3': process_callback_button3
    }

    current_level_function = levels[current_level]

    await current_level_function(
        call, id=id
    )
