import aiogram
from aiogram.dispatcher import FSMContext

import data
import states
from data import moder_chat_id
from main import bot, dp
from keyboard import menu_cd, is_correct_keyboard, check_markup, reject_keyboard
from aiogram import types, Dispatcher
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
    text_val = message.html_text
    await state.update_data(answer2=text_val)

    letter = models.Letter()

    letter.recipient_username = username
    letter.text = text_val
    letter.type = 'TEXT'
    letter.sender_id = message.from_user.id

    letter = await letter.create()

    await state.update_data(letter_id=letter.id)

    await message.answer('Я всё правильно понял?')
    await message.answer(f'Твоя валентинка будет отправлена пользователю {username}')
    await message.answer('Текст валентинки: ')
    keyboard = await is_correct_keyboard(letter)
    await message.answer(text_val, reply_markup=keyboard, parse_mode="HTML")

    await states.Letter.endpoint.set()


@dp.message_handler(state=states.Letter.q_text_val, content_types=['photo'])
async def text_val_answer(message: types.Message, state: FSMContext):
    data = await state.get_data()
    username = data.get('answer1')
    text_val = message.photo[-1].file_id
    await state.update_data(answer2=text_val)
    letter = models.Letter()
    letter.recipient_username = username
    letter.file_id = text_val
    letter.type = "PHOTO"
    letter.text = message.caption
    letter.sender_id = message.from_user.id
    letter = await letter.create()
    await state.update_data(letter_id=letter.id)
    await message.answer('Я всё правильно понял?')
    await message.answer(f'Твоя валентинка будет отправлена пользователю {username}')
    keyboard = await is_correct_keyboard(letter)
    await message.answer_photo(photo=letter.file_id, caption=letter.text)
    await message.answer('Ваше фото', reply_markup=keyboard)

    await states.Letter.endpoint.set()


@dp.message_handler(state=states.Letter.q_text_val, content_types=['video'])
async def text_val_answer(message: types.Message, state: FSMContext):
    data = await state.get_data()
    username = data.get('answer1')
    text_val = message.video.file_id
    await state.update_data(answer2=text_val)
    letter = models.Letter()
    letter.recipient_username = username
    letter.file_id = text_val
    letter.text = message.caption
    letter.type = 'VIDEO'
    letter.sender_id = message.from_user.id
    letter = await letter.create()
    await state.update_data(letter_id=letter.id)
    await message.answer('Я всё правильно понял?')
    await message.answer(f'Твоя валентинка будет отправлена пользователю {username}')
    keyboard = await is_correct_keyboard(letter)
    await message.answer_video(video=letter.file_id, caption=letter.text)
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
    letter.file_id = text_val
    letter.type = 'GIF'
    letter.sender_id = message.from_user.id
    letter = await letter.create()
    await state.update_data(letter_id=letter.id)
    await message.answer('Я всё правильно понял?')
    await message.answer(f'Твоя валентинка будет отправлена пользователю {username}')
    keyboard = await is_correct_keyboard(letter)
    await message.answer_animation(animation=letter.file_id)
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
    letter.file_id = text_val
    letter.type = 'STICKER'
    letter.sender_id = message.from_user.id
    letter = await letter.create()
    await state.update_data(letter_id=letter.id)
    await message.answer('Я всё правильно понял?')
    await message.answer(f'Твоя валентинка будет отправлена пользователю {username}')
    keyboard = await is_correct_keyboard(letter)
    await message.answer_sticker(sticker=letter.file_id)
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
    letter.file_id = text_val
    letter.type = "VOICE"
    letter.sender_id = message.from_user.id
    letter = await letter.create()
    await state.update_data(letter_id=letter.id)
    await message.answer('Я всё правильно понял?')
    await message.answer(f'Твоя валентинка будет отправлена пользователю {username}')
    keyboard = await is_correct_keyboard(letter)
    await message.answer_voice(voice=letter.file_id)
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
    letter.file_id = text_val
    letter.type = 'AUDIO'
    letter.sender_id = message.from_user.id
    letter = await letter.create()
    await state.update_data(letter_id=letter.id)
    await message.answer('Я всё правильно понял?')
    await message.answer(f'Твоя валентинка будет отправлена пользователю {username}')
    keyboard = await is_correct_keyboard(letter)
    await message.answer_audio(audio=letter.file_id)
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
    letter.file_id = text_val
    letter.type = 'VIDEO_NOTE'
    letter.sender_id = message.from_user.id
    letter = await letter.create()
    await state.update_data(letter_id=letter.id)
    await message.answer('Я всё правильно понял?')
    await message.answer(f'Твоя валентинка будет отправлена пользователю {username}')
    keyboard = await is_correct_keyboard(letter)
    await message.answer_video_note(video_note=letter.file_id)
    await message.answer('Ваша песня', reply_markup=keyboard)

    await states.Letter.endpoint.set()


@dp.message_handler(state=states.Letter.correct_username)
async def text_val_answer1(message: types.Message, state: FSMContext):
    data = await state.get_data()
    username = message.text
    await state.update_data(answer1=username)
    text_val = data.get('answer2')
    letter_id = data.get("letter_id")
    if message.forward_from:
        # await state.update_data(answer1=str(message.from_user.id))
        username = str(message.forward_from.id)
    elif message.text.startswith('@') or message.text.startswith('+'):
        username = message.text
        await state.update_data(answer1=username)
        await message.answer('Супер! Мы нашли его! Теперь мы ждём текст твоей валентинки🧐')
        await states.Letter.q_text_val.set()
    else:
        await message.answer(
            'Некорректный запрос. Если вы переслали сообщение, то профиль получателя закрыт, если юзернейм,'
            'то он должен начинаться с @. Если вы хотите написать номер, то он должен начинаться с +')

    await message.answer('Я всё правильно понял?')
    await message.answer(f'Твоя валентинка будет отправлена пользователю {username}')


    letter = await models.Letter.get(letter_id)

    letter.recipient_username = username
    # letter.text = text_val
    letter.sender_id = message.from_user.id

    await letter.update(recipient_username=username).apply()

    keyboard = await is_correct_keyboard(letter)

    if letter.type == "PHOTO":
        await message.answer_photo(photo=letter.file_id, caption=letter.text, parse_mode="HTML")
        await message.answer('Ваше фото', reply_markup=keyboard)
    elif letter.type == 'VIDEO':
        await message.answer_video(video=letter.file_id, caption=letter.text, parse_mode="HTML")
        await message.answer('Ваше видео', reply_markup=keyboard)
    elif letter.type == 'GIF':
        await message.answer_animation(animation=letter.file_id)
        await message.answer('Ваша гифка', reply_markup=keyboard)
    elif letter.type == 'STICKER':
        await message.answer_sticker(sticker=letter.file_id)
        await message.answer('Ваш стикер', reply_markup=keyboard)
    elif letter.type == 'VOICE':
        await message.answer_voice(voice=letter.file_id)
        await message.answer('Ваше голосовое', reply_markup=keyboard)
    elif letter.type == 'VIDEO_NOTE':
        await message.answer_video_note(video_note=letter.file_id)
        await message.answer('Ваше видеосообщение', reply_markup=keyboard)
    elif letter.type == 'AUDIO':
        await message.answer_audio(audio=letter.file_id)
        await message.answer('Ваша песня', reply_markup=keyboard)
    elif letter.type == 'TEXT':
        await message.answer(text=letter.text, parse_mode="HTML")
        await message.answer('Ваш текст', reply_markup=keyboard)




    await states.Letter.endpoint.set()


'''Блок хендлеров для измененения валентинки'''


@dp.message_handler(state=states.Letter.correct_val, content_types=['text'])
async def text_val_answer(message: types.Message, state: FSMContext):
    data = await state.get_data()
    username = data.get('answer1')
    text_val = message.html_text
    letter_id = data.get("letter_id")
    await state.update_data(answer2=text_val)
    await message.answer('Я всё правильно понял?')
    await message.answer(f'Твоя валентинка будет отправлена пользователю {username}')
    await message.answer('Текст валентинки: ')
    letter = await models.Letter.get(letter_id)
    letter.recipient_username = username
    letter.sender_id = message.from_user.id
    await letter.update(text=text_val, type='TEXT').apply()
    keyboard = await is_correct_keyboard(letter)
    await message.answer(text_val, reply_markup=keyboard, parse_mode="HTML")
    await states.Letter.endpoint.set()


@dp.message_handler(state=states.Letter.correct_val, content_types=['photo'])
async def text_val_answer(message: types.Message, state: FSMContext):
    data = await state.get_data()
    username = data.get('answer1')
    text_val = message.photo[-1].file_id
    letter_id = data.get("letter_id")
    await state.update_data(answer2=text_val)
    await message.answer('Я всё правильно понял?')
    await message.answer(f'Твоя валентинка будет отправлена пользователю {username}')
    letter = await models.Letter.get(letter_id)
    letter.recipient_username = username
    await letter.update(text=message.caption, file_id=text_val, type='PHOTO').apply()
    keyboard = await is_correct_keyboard(letter)
    await message.answer_photo(photo=letter.file_id, caption=letter.text)
    await message.answer('Ваше фото', reply_markup=keyboard)
    await states.Letter.endpoint.set()


@dp.message_handler(state=states.Letter.correct_val, content_types=['video'])
async def text_val_answer(message: types.Message, state: FSMContext):
    data = await state.get_data()
    username = data.get('answer1')
    text_val = message.video.file_id
    letter_id = data.get("letter_id")
    await state.update_data(answer2=text_val)
    await message.answer('Я всё правильно понял?')
    await message.answer(f'Твоя валентинка будет отправлена пользователю {username}')
    letter = await models.Letter.get(letter_id)
    letter.recipient_username = username
    await letter.update(text=message.caption, file_id=text_val, type='VIDEO').apply()
    keyboard = await is_correct_keyboard(letter)
    await message.answer_video(video=letter.file_id, caption=letter.text)
    await message.answer('Ваше видео', reply_markup=keyboard)
    await states.Letter.endpoint.set()


@dp.message_handler(state=states.Letter.correct_val, content_types=['animation'])
async def text_val_answer(message: types.Message, state: FSMContext):
    data = await state.get_data()
    username = data.get('answer1')
    text_val = message.animation.file_id
    letter_id = data.get("letter_id")
    await state.update_data(answer2=text_val)
    await message.answer('Я всё правильно понял?')
    await message.answer(f'Твоя валентинка будет отправлена пользователю {username}')
    letter = await models.Letter.get(letter_id)
    letter.recipient_username = username
    await letter.update(file_id=text_val, type='GIF').apply()
    keyboard = await is_correct_keyboard(letter)
    await message.answer_animation(animation=letter.file_id)
    await message.answer('Ваша гифка', reply_markup=keyboard)
    await states.Letter.endpoint.set()


@dp.message_handler(state=states.Letter.correct_val, content_types=['voice'])
async def text_val_answer(message: types.Message, state: FSMContext):
    data = await state.get_data()
    username = data.get('answer1')
    text_val = message.voice.file_id
    letter_id = data.get("letter_id")
    await state.update_data(answer2=text_val)
    await message.answer('Я всё правильно понял?')
    await message.answer(f'Твоя валентинка будет отправлена пользователю {username}')
    letter = await models.Letter.get(letter_id)
    letter.recipient_username = username
    await letter.update(file_id=text_val, type='VOICE').apply()
    keyboard = await is_correct_keyboard(letter)
    await message.answer_voice(voice=letter.file_id)
    await message.answer('Ваше голосовое', reply_markup=keyboard)
    await states.Letter.endpoint.set()


@dp.message_handler(state=states.Letter.correct_val, content_types=['sticker'])
async def text_val_answer(message: types.Message, state: FSMContext):
    data = await state.get_data()
    username = data.get('answer1')
    text_val = message.sticker.file_id
    letter_id = data.get("letter_id")
    await state.update_data(answer2=text_val)
    await message.answer('Я всё правильно понял?')
    await message.answer(f'Твоя валентинка будет отправлена пользователю {username}')
    letter = await models.Letter.get(letter_id)
    letter.recipient_username = username
    await letter.update(file_id=text_val, type='STICKER').apply()
    keyboard = await is_correct_keyboard(letter)
    await message.answer_sticker(sticker=letter.file_id)
    await message.answer('Ваш стикер', reply_markup=keyboard)
    await states.Letter.endpoint.set()


@dp.message_handler(state=states.Letter.correct_val, content_types=['video_note'])
async def text_val_answer(message: types.Message, state: FSMContext):
    data = await state.get_data()
    username = data.get('answer1')
    text_val = message.video_note.file_id
    letter_id = data.get("letter_id")
    await state.update_data(answer2=text_val)
    await message.answer('Я всё правильно понял?')
    await message.answer(f'Твоя валентинка будет отправлена пользователю {username}')
    letter = await models.Letter.get(letter_id)
    letter.recipient_username = username
    await letter.update(file_id=text_val, type='VIDEO_NOTE').apply()
    keyboard = await is_correct_keyboard(letter)
    await message.answer_video_note(video_note=letter.file_id)
    await message.answer('Ваше видеосообщение', reply_markup=keyboard)
    await states.Letter.endpoint.set()


@dp.message_handler(state=states.Letter.correct_val, content_types=['audio'])
async def text_val_answer(message: types.Message, state: FSMContext):
    data = await state.get_data()
    username = data.get('answer1')
    text_val = message.audio.file_id
    letter_id = data.get("letter_id")
    await state.update_data(answer2=text_val)
    await message.answer('Я всё правильно понял?')
    await message.answer(f'Твоя валентинка будет отправлена пользователю {username}')
    letter = await models.Letter.get(letter_id)
    letter.recipient_username = username
    await letter.update(file_id=text_val, type='AUDIO').apply()
    keyboard = await is_correct_keyboard(letter)
    await message.answer_audio(audio=letter.file_id)
    await message.answer('Ваша пэсня', reply_markup=keyboard)
    await states.Letter.endpoint.set()


async def process_callback_button1(callback_query: types.CallbackQuery, **kwargs):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Отправь исправленный юзернейм')
    await states.Letter.correct_username.set()
    await callback_query.message.delete_reply_markup()


async def process_callback_button2(callback_query: types.CallbackQuery, **kwargs):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Отправь новую валентинку')
    await states.Letter.correct_val.set()
    await callback_query.message.delete_reply_markup()


async def process_callback_button3(callback_query: types.CallbackQuery, id, **kwargs):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id,
                           'Отправили! Чтобы прислать мне ещё одну валентинку пришли мне любое сообщение либо нажми на /new)')
    letter = await postgres.get_letter(int(id))
    await callback_query.message.delete_reply_markup()
    await bot.send_message(moder_chat_id, f'Юзернейм: \n{letter.recipient_username}\nВалентинка: ')
    if letter.type == "PHOTO":
        await bot.send_photo(chat_id=moder_chat_id, photo=letter.file_id, caption=letter.text, parse_mode="HTML")
    elif letter.type == 'VIDEO':
        await bot.send_video(chat_id=moder_chat_id, video=letter.file_id, caption=letter.text, parse_mode="HTML")
    elif letter.type == 'GIF':
        await bot.send_animation(chat_id=moder_chat_id, animation=letter.file_id)
    elif letter.type == 'STICKER':
        await bot.send_sticker(chat_id=moder_chat_id, sticker=letter.file_id)
    elif letter.type == 'VOICE':
        await bot.send_voice(chat_id=moder_chat_id, voice=letter.file_id)
    elif letter.type == 'VIDEO_NOTE':
        await bot.send_video_note(chat_id=moder_chat_id, video_note=letter.file_id)
    elif letter.type == 'AUDIO':
        await bot.send_audio(chat_id=moder_chat_id, audio=letter.file_id)
    elif letter.type == 'TEXT':
        await bot.send_message(chat_id=moder_chat_id, text=letter.text, parse_mode="HTML")
    keyboard = await check_markup(letter)
    await bot.send_message(chat_id=moder_chat_id, text="Что сделать?", reply_markup=keyboard)

    await states.Letter.startpoint.set()


async def add_contact(call: types.CallbackQuery, id, **kwargs):
    user = types.User.get_current()
    user_in_DB: models.User = await postgres.get_user(user.id)
    await call.message.edit_text("Пришли айди или юзернейм получателя")
    await states.Letter.add_receiver_contact.set()
    state = Dispatcher.get_current().current_state()
    await state.update_data(letter_id=id)
    # if user_in_DB:
    # if not user_in_DB.is_bot_blocked:
    # if user_in_DB.is_admin:


@dp.message_handler(state=states.Letter.add_receiver_contact)
async def get_username_from_admin(message: types.Message, state: FSMContext):
    print("ok")
    data = await state.get_data()
    letter: models.Letter = data.get("letter_id")
    # letter.recipient_username
    # letter.recipient_id
    keyboard = await check_markup(letter)
    await message.answer(text="Что сделать?", reply_markup=keyboard)


async def initialisate_chat_with_user(call: types.CallbackQuery, id, **kwargs):
    user = types.User.get_current()
    user_in_DB: models.User = await postgres.get_user(user.id)
    if user.id == data.userbot_id:

        await call.message.edit_text("Пришли айди или юзернейм получателя")
        await states.Letter.add_receiver_contact.set()
        state = Dispatcher.get_current().current_state()
        await state.update_data(letter_id=id)
    else:
        await bot.answer_callback_query(callback_query_id=call.id, text="Эту кнопку должен нажать акк юзербота",
                                        show_alert=True)


async def reject_letter(call: types.CallbackQuery, id, **kwargs):
    user = types.User.get_current()
    user_in_DB: models.User = await postgres.get_user(user.id)

    letter = await postgres.get_letter(int(id))
    keyboard = await reject_keyboard(letter=letter)
    await call.message.edit_text("Напиши причину отказа", reply_markup=keyboard)
    '''
    await states.Letter.add_receiver_contact.set()
    state = Dispatcher.get_current().current_state()
    await state.update_data(letter_id=id)
    '''


async def admin_menu(call: types.CallbackQuery, id, **kwargs):
    user = types.User.get_current()
    user_in_DB: models.User = await postgres.get_user(user.id)
    letter = await postgres.get_letter(int(id))
    keyboard = await check_markup(letter)
    await call.message.edit_text(text="Что сделать?", reply_markup=keyboard)


@dp.callback_query_handler(menu_cd.filter(), state='*')
async def navigate(call: types.CallbackQuery, callback_data: dict):
    current_level = callback_data.get('level')
    id = callback_data.get('id')

    levels = {
        '1': process_callback_button1,
        '2': process_callback_button2,
        '3': process_callback_button3,
        '4': add_contact,
        '5': initialisate_chat_with_user,
        '6': reject_letter,
        '7': admin_menu,
    }

    current_level_function = levels[current_level]

    await current_level_function(
        call, id=id
    )


@dp.message_handler(lambda msg: msg.from_user.id == USERBOT)
async def userbot_connect(message: types.Message):
    user = types.User.get_current()
    user_in_DB: User = await get_user(user.id)
    if user_in_DB:
        if not user_in_DB.is_bot_blocked:
            if user_in_DB.is_admin:
                if message.text.startswith("/#"):
                    message_dict = message.text[2:].split(":")
                    if message_dict[0] == "s":
                        # succesfull delivery
                        letter: Letter = await get_letter(int(message_dict[1]))

                        letter.status = "DELIVERED"
                        await letter.update(status="DELIVERED").apply()

                        await bot.send_message(chat_id=letter.sender_id,
                                               text=f"Твоя валентинка успешно доставлена получателю",
                                               reply_to_message_id=letter.sender_message_id)
                        alert_mess_text = f"🟢🟢🟢\nНовая валентинка\n\nПолучатель: "
                        if letter.recipient_id != None:

                            alert_mess_text += f'<a href="tg://user?id={str(letter.recipient_id)}">{str(letter.recipient_fullname)}</a>'
                        elif letter.recipient_username != None:
                            alert_mess_text += f"@{letter.recipient_username}"
                        elif letter.recipient_phone_number != None:
                            alert_mess_text += f"<code>{letter.recipient_phone_number}</code>\nСодержание:"
                        await bot.edit_message_text(chat_id=ADMINS, message_id=int(letter.admin_message_id),
                                                    text=alert_mess_text)
                    elif message_dict[0] == "e":
                        # error delivery
                        letter: Letter = await get_letter(int(message_dict[1]))

                        letter.status = "ERROR"
                        await letter.update(status="ERROR").apply()

                        await bot.send_message(chat_id=letter.sender_id,
                                               text=f"К сожалению во время отправки твоей валентинки возникла ошибки, попробуй еще раз",
                                               reply_to_message_id=letter.sender_message_id)
                        alert_mess_text = f"❌❌❌\nНовая валентинка\n\nПолучатель: "
                        if letter.recipient_id != None:

                            alert_mess_text += f'<a href="tg://user?id={str(letter.recipient_id)}">{str(letter.recipient_fullname)}</a>'
                        elif letter.recipient_username != None:
                            alert_mess_text += f"@{letter.recipient_username}"
                        elif letter.recipient_phone_number != None:
                            alert_mess_text += f"<code>{letter.recipient_phone_number}</code>\nСодержание:"
                        await bot.edit_message_text(chat_id=ADMINS, message_id=int(letter.admin_message_id),
                                                    text=alert_mess_text)
                    elif message_dict[0] == "a":
                        answer: Answer = await get_answer(int(message_dict[1]))
                        try:
                            if answer.type != "TEXT" and message.reply_to_message != None:
                                answer.file_id_bot = await get_file_id(answer, message.reply_to_message)
                            mess_id = await send_answer(letter=answer, chat_id=answer.recipient_id)
                            answer.status = "DELIVERED"
                            answer.recipient_message_id = mess_id.message_id
                            await answer.update(status="DELIVERED", file_id_bot=answer.file_id_bot,
                                                recipient_message_id=answer.recipient_message_id).apply()
                        except:

                            answer.status = "ERROR"
                            await answer.update(status="ERROR").apply()
