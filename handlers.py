import aiogram
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

    if not message.from_user.id in users:
        # Срабатывает, если пользователя нет в дб и добавляет его туда
        await message.answer("Привет! Я бот, который отправляет поздравления другим людям!")
        await postgres.create_user(message.from_user.id)  #

    await message.answer('Отправь нам @юзернейм твоей радости🥰')
    await states.Letter.q_username.set()


@dp.message_handler(state=states.Letter.startpoint)
async def startpoint_handler(message: types.Message):
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


@dp.message_handler(state=states.Letter.q_text_val, content_types=['text'])
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

    await states.Letter.endpoint.set()

@dp.message_handler(state=states.Letter.q_text_val, content_types=['photo'])
async def text_val_answer(message: types.Message, state: FSMContext):
    data = await state.get_data()
    username = data.get('answer1')
    text_val = message.photo[-1].file_id
    await state.update_data(answer2=text_val)
    letter = models.Letter()
    letter.recipient_username = username
    letter.photo = text_val
    letter.text = message.caption
    letter.sender_id = message.from_user.id
    letter = await letter.create()
    await state.update_data(letter_id=letter.id)
    await message.answer('Я всё правильно понял?')
    await message.answer(f'Твоя валентинка будет отправлена пользователю {username}')
    keyboard = await is_correct_keyboard(letter)
    await bot.send_photo(message.from_user.id, letter.photo)
    try:
        await bot.send_message(message.from_user.id, letter.text)
    except aiogram.utils.exceptions.MessageTextIsEmpty:
        pass
    await message.answer('Ваше фото (можете добавить к нему текст)', reply_markup=keyboard)

    await states.Letter.endpoint.set()


@dp.message_handler(state=states.Letter.q_text_val, content_types=['video'])
async def text_val_answer(message: types.Message, state: FSMContext):

    data = await state.get_data()
    username = data.get('answer1')
    text_val = message.video.file_id
    await state.update_data(answer2=text_val)
    letter = models.Letter()
    letter.recipient_username = username
    letter.video = text_val
    letter.sender_id = message.from_user.id
    letter = await letter.create()
    await state.update_data(letter_id=letter.id)
    await message.answer('Я всё правильно понял?')
    await message.answer(f'Твоя валентинка будет отправлена пользователю {username}')
    keyboard = await is_correct_keyboard(letter)
    await bot.send_video(message.from_user.id, letter.video)
    await message.answer('Ваше видео', reply_markup=keyboard)

    await states.Letter.endpoint.set()

@dp.message_handler(state=states.Letter.q_text_val, content_types=['animation'])
async def text_val_answer(message: types.Message, state: FSMContext):

    data = await state.get_data()
    username = data.get('answer1')
    text_val = message.animation.file_id
    await state.update_data(answer2=text_val)
    letter = models.Letter()
    letter.recipient_username = username
    letter.gif = text_val
    letter.sender_id = message.from_user.id
    letter = await letter.create()
    await state.update_data(letter_id=letter.id)
    await message.answer('Я всё правильно понял?')
    await message.answer(f'Твоя валентинка будет отправлена пользователю {username}')
    keyboard = await is_correct_keyboard(letter)
    await bot.send_animation(message.from_user.id, letter.gif)
    await message.answer('Ваша гифка', reply_markup=keyboard)

    await states.Letter.endpoint.set()

@dp.message_handler(state=states.Letter.q_text_val, content_types=['sticker'])
async def text_val_answer(message: types.Message, state: FSMContext):

    data = await state.get_data()
    username = data.get('answer1')
    text_val = message.sticker.file_id
    await state.update_data(answer2=text_val)
    letter = models.Letter()
    letter.recipient_username = username
    letter.sticker = text_val
    letter.sender_id = message.from_user.id
    letter = await letter.create()
    await state.update_data(letter_id=letter.id)
    await message.answer('Я всё правильно понял?')
    await message.answer(f'Твоя валентинка будет отправлена пользователю {username}')
    keyboard = await is_correct_keyboard(letter)
    await bot.send_sticker(message.from_user.id, letter.sticker)
    await message.answer('Ваш стикер', reply_markup=keyboard)

    await states.Letter.endpoint.set()

@dp.message_handler(state=states.Letter.q_text_val, content_types=['voice'])
async def text_val_answer(message: types.Message, state: FSMContext):

    data = await state.get_data()
    username = data.get('answer1')
    text_val = message.voice.file_id
    await state.update_data(answer2=text_val)
    letter = models.Letter()
    letter.recipient_username = username
    letter.voice = text_val
    letter.sender_id = message.from_user.id
    letter = await letter.create()
    await state.update_data(letter_id=letter.id)
    await message.answer('Я всё правильно понял?')
    await message.answer(f'Твоя валентинка будет отправлена пользователю {username}')
    keyboard = await is_correct_keyboard(letter)
    await bot.send_voice(message.from_user.id, letter.voice)
    await message.answer('Ваше голосовое сообщение', reply_markup=keyboard)

    await states.Letter.endpoint.set()

@dp.message_handler(state=states.Letter.q_text_val, content_types=['audio'])
async def text_val_answer(message: types.Message, state: FSMContext):

    data = await state.get_data()
    username = data.get('answer1')
    text_val = message.audio.file_id
    await state.update_data(answer2=text_val)
    letter = models.Letter()
    letter.recipient_username = username
    letter.audio = text_val
    letter.sender_id = message.from_user.id
    letter = await letter.create()
    await state.update_data(letter_id=letter.id)
    await message.answer('Я всё правильно понял?')
    await message.answer(f'Твоя валентинка будет отправлена пользователю {username}')
    keyboard = await is_correct_keyboard(letter)
    await bot.send_audio(message.from_user.id, letter.audio)
    await message.answer('Ваша песня', reply_markup=keyboard)

    await states.Letter.endpoint.set()

@dp.message_handler(state=states.Letter.q_text_val, content_types=['video_note'])
async def text_val_answer(message: types.Message, state: FSMContext):

    data = await state.get_data()
    username = data.get('answer1')
    text_val = message.video_note.file_id
    await state.update_data(answer2=text_val)
    letter = models.Letter()
    letter.recipient_username = username
    letter.video_note = text_val
    letter.sender_id = message.from_user.id
    letter = await letter.create()
    await state.update_data(letter_id=letter.id)
    await message.answer('Я всё правильно понял?')
    await message.answer(f'Твоя валентинка будет отправлена пользователю {username}')
    keyboard = await is_correct_keyboard(letter)
    await bot.send_video_note(message.from_user.id, letter.video_note)
    await message.answer('Ваша песня', reply_markup=keyboard)

    await states.Letter.endpoint.set()

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

    await states.Letter.endpoint.set()


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

    await states.Letter.endpoint.set()


async def process_callback_button1(callback_query: types.CallbackQuery, **kwargs):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Отправь исправленный юзернейм')
    await states.Letter.correct_username.set()


async def process_callback_button2(callback_query: types.CallbackQuery, **kwargs):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Отправь новую валентинку')
    await states.Letter.correct_val.set()



async def process_callback_button3(callback_query: types.CallbackQuery, id, **kwargs):


    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Отправили! Чтобы прислать мне ещё одну валентинку пришли мне любое сообщение либо нажми на /new)')
    letter = await postgres.get_letter(int(id))
    await bot.send_message(moder_chat_id, 'Юзернейм')
    await bot.send_message(moder_chat_id, letter.recipient_username)
    await bot.send_message(moder_chat_id, 'Текст валентинки')
    if letter.text or letter.photo:
        try:
            await bot.send_photo(moder_chat_id, letter.photo)
        except aiogram.utils.exceptions.BadRequest:
            pass
        try:
            await bot.send_message(moder_chat_id, letter.text)
        except aiogram.utils.exceptions.MessageTextIsEmpty:
            pass
    elif letter.video:
        await bot.send_video(moder_chat_id, letter.video)
    elif letter.gif:
        await bot.send_animation(moder_chat_id, letter.gif)
    elif letter.sticker:
        await bot.send_sticker(moder_chat_id, letter.sticker)
    elif letter.voice:
        await bot.send_voice(moder_chat_id, letter.voice)
    elif letter.audio:
        await bot.send_audio(moder_chat_id, letter.audio)
    elif letter.video_note:
        await bot.send_video_note(moder_chat_id, letter.video_note)

    await states.Letter.startpoint.set()



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
