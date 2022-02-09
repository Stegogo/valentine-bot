import aiogram
from aiogram.dispatcher import FSMContext
import states
from data import moder_chat_id
from main import bot, dp
from keyboard import menu_cd, is_correct_keyboard
from aiogram import types
import postgres
import models

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    users = await postgres.get_users(1)

    if not message.from_user.id in users:
        # Срабатывает, если пользователя нет в дб и добавляет его туда
        await message.answer("Привет! Я бот, который отправляет поздравления другим людям!")
        await postgres.create_user(message.from_user.id)  #

    await message.answer(
        'Отправь нам @юзернейм или телефон твоей радости🥰. Можешь также переслать ее сообщение, если ее профиль открыт.')
    await states.Letter.q_username.set()


@dp.message_handler(state=states.Letter.startpoint)
async def startpoint_handler(message: types.Message):
    await message.answer(
        'Отправь нам @юзернейм или телефон твоей радости🥰. Можешь также переслать ее сообщение, если ее профиль открыт.')
    await states.Letter.q_username.set()


@dp.message_handler(state=states.Letter.q_username)
async def username_answer(message: types.Message, state: FSMContext):
    username = message.text

    if message.forward_from:
        if message.forward_from.username:
            await state.update_data(recipient_username=str(message.forward_from.username),
                                    recipient_id=int(message.forward_from.id))
            await message.answer('Супер! Мы нашли его! Теперь мы ждём текст твоей валентинки🧐')
            await states.Letter.q_text_val.set()
        else:
            await state.update_data(recipient_id=int(message.forward_from.id))
            await message.answer('Супер! Мы нашли его! Теперь мы ждём текст твоей валентинки🧐')
            await states.Letter.q_text_val.set()
    elif username.startswith('@'):
        await state.update_data(recipient_username=username)
        await message.answer('Супер! Мы нашли его! Теперь мы ждём текст твоей валентинки🧐')
        await states.Letter.q_text_val.set()
    elif username.startswith('+'):
        await state.update_data(recipient_phone_number=username)
        await message.answer('Супер! Мы нашли его! Теперь мы ждём текст твоей валентинки🧐')
        await states.Letter.q_text_val.set()
    else:
        await message.answer(
            'Некорректный запрос. Если вы переслали сообщение, то профиль получателя закрыт, если юзернейм,'
            'то он должен начинаться с @. Если вы хотите написать номер, то он должен начинаться с +')


@dp.message_handler(state=states.Letter.q_text_val, content_types=['text'])
async def text_val_answer(message: types.Message, state: FSMContext):

    data = await state.get_data()
    username = data.get('answer1')
    text_val = message.html_text
    await state.update_data(answer2=text_val)

    # try
    recipient_username = data.get('recipient_username')
    recipient_id = data.get('recipient_id')
    recipient_phone_number = data.get('recipient_phone_number')

    letter = models.Letter()

    if recipient_username and recipient_id:
        letter.recipient_username = recipient_username
        letter.recipient_id = recipient_id
        username = recipient_username
    elif recipient_id:
        letter.recipient_id = recipient_id
        username = recipient_id
    elif recipient_username:
        letter.recipient_username = recipient_username
        username = recipient_username
    elif recipient_phone_number:
        letter.recipient_phone_number = recipient_phone_number
        username = recipient_phone_number
    else:
        print("problem")

    letter.type = 'TEXT'
    letter.text = text_val
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

    # try
    recipient_username = data.get('recipient_username')
    recipient_id = data.get('recipient_id')
    recipient_phone_number = data.get('recipient_phone_number')

    letter = models.Letter()

    if recipient_username and recipient_id:
        letter.recipient_username = recipient_username
        letter.recipient_id = recipient_id
        username = recipient_username
    elif recipient_id:
        letter.recipient_id = recipient_id
        username = recipient_id
    elif recipient_username:
        letter.recipient_username = recipient_username
        username = recipient_username
    elif recipient_phone_number:
        letter.recipient_phone_number = recipient_phone_number
        username = recipient_phone_number
    else:
        print("problem")


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

    text_val = message.video.file_id

    data = await state.get_data()
    await state.update_data(answer2=text_val)

    # try
    recipient_username = data.get('recipient_username')
    recipient_id = data.get('recipient_id')
    recipient_phone_number = data.get('recipient_phone_number')

    letter = models.Letter()

    if recipient_username and recipient_id:
        letter.recipient_username = recipient_username
        letter.recipient_id = recipient_id
        username = recipient_username
    elif recipient_id:
        letter.recipient_id = recipient_id
        username = recipient_id
    elif recipient_username:
        letter.recipient_username = recipient_username
        username = recipient_username
    elif recipient_phone_number:
        letter.recipient_phone_number = recipient_phone_number
        username = recipient_phone_number
    else:
        print("problem")

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

    text_val = message.animation.file_id

    data = await state.get_data()
    await state.update_data(answer2=text_val)

    # try
    recipient_username = data.get('recipient_username')
    recipient_id = data.get('recipient_id')
    recipient_phone_number = data.get('recipient_phone_number')

    letter = models.Letter()

    if recipient_username and recipient_id:
        letter.recipient_username = recipient_username
        letter.recipient_id = recipient_id
        username = recipient_username
    elif recipient_id:
        letter.recipient_id = recipient_id
        username = recipient_id
    elif recipient_username:
        letter.recipient_username = recipient_username
        username = recipient_username
    elif recipient_phone_number:
        letter.recipient_phone_number = recipient_phone_number
        username = recipient_phone_number
    else:
        print("problem")

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

    text_val = message.sticker.file_id

    data = await state.get_data()
    await state.update_data(answer2=text_val)

    # try
    recipient_username = data.get('recipient_username')
    recipient_id = data.get('recipient_id')
    recipient_phone_number = data.get('recipient_phone_number')

    letter = models.Letter()

    if recipient_username and recipient_id:
        letter.recipient_username = recipient_username
        letter.recipient_id = recipient_id
        username = recipient_username
    elif recipient_id:
        letter.recipient_id = recipient_id
        username = recipient_id
    elif recipient_username:
        letter.recipient_username = recipient_username
        username = recipient_username
    elif recipient_phone_number:
        letter.recipient_phone_number = recipient_phone_number
        username = recipient_phone_number
    else:
        print("problem")

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

    text_val = message.voice.file_id

    data = await state.get_data()
    await state.update_data(answer2=text_val)

    # try
    recipient_username = data.get('recipient_username')
    recipient_id = data.get('recipient_id')
    recipient_phone_number = data.get('recipient_phone_number')

    letter = models.Letter()

    if recipient_username and recipient_id:
        letter.recipient_username = recipient_username
        letter.recipient_id = recipient_id
        username = recipient_username
    elif recipient_id:
        letter.recipient_id = recipient_id
        username = recipient_id
    elif recipient_username:
        letter.recipient_username = recipient_username
        username = recipient_username
    elif recipient_phone_number:
        letter.recipient_phone_number = recipient_phone_number
        username = recipient_phone_number
    else:
        print("problem")

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
    text_val = message.audio.file_id

    data = await state.get_data()
    await state.update_data(answer2=text_val)

    # try
    recipient_username = data.get('recipient_username')
    recipient_id = data.get('recipient_id')
    recipient_phone_number = data.get('recipient_phone_number')

    letter = models.Letter()

    if recipient_username and recipient_id:
        letter.recipient_username = recipient_username
        letter.recipient_id = recipient_id
        username = recipient_username
    elif recipient_id:
        letter.recipient_id = recipient_id
        username = recipient_id
    elif recipient_username:
        letter.recipient_username = recipient_username
        username = recipient_username
    elif recipient_phone_number:
        letter.recipient_phone_number = recipient_phone_number
        username = recipient_phone_number
    else:
        print("problem")

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
    text_val = message.video_note.file_id

    data = await state.get_data()
    await state.update_data(answer2=text_val)

    # try
    recipient_username = data.get('recipient_username')
    recipient_id = data.get('recipient_id')
    recipient_phone_number = data.get('recipient_phone_number')

    letter = models.Letter()

    if recipient_username and recipient_id:
        letter.recipient_username = recipient_username
        letter.recipient_id = recipient_id
        username = recipient_username
    elif recipient_id:
        letter.recipient_id = recipient_id
        username = recipient_id
    elif recipient_username:
        letter.recipient_username = recipient_username
        username = recipient_username
    elif recipient_phone_number:
        letter.recipient_phone_number = recipient_phone_number
        username = recipient_phone_number
    else:
        print("problem")

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
    text_val = data.get('answer2')
    letter_id = data.get("letter_id")

    letter = await models.Letter.get(letter_id)

    recipient_username = data.get('recipient_username')
    recipient_id = data.get('recipient_id')
    recipient_phone_number = data.get('recipient_phone_number')


    if recipient_username and recipient_id:
        username = recipient_username
    elif recipient_id:
        username = recipient_id
    elif recipient_username:
        username = recipient_username
    elif recipient_phone_number:
        username = recipient_phone_number
    else:
        print("problem")

    if message.forward_from:
        if message.forward_from.username:
            await state.update_data(recipient_username=str(message.forward_from.username),
                                    recipient_id=int(message.forward_from.id))
            await message.answer('Супер! Мы нашли его!')
            await letter.update(recipient_username=str(message.forward_from.username)).apply()

        else:
            await state.update_data(recipient_id=int(message.forward_from.id))
            await letter.update(recipient_id=int(message.forward_from.id)).apply()
            await message.answer('Супер!')


        await states.Letter.endpoint.set()

    elif message.text.startswith('@'):
        await state.update_data(recipient_username=username)
        await letter.update(recipient_username=username).apply()
        await message.answer('Супер! Мы нашли его!')
        await states.Letter.endpoint.set()

    elif message.text.startswith('+'):
        await state.update_data(recipient_phone_number=username)
        await letter.update(recipient_phone_number=username).apply()
        await message.answer('Супер! Мы нашли его!')
        await states.Letter.endpoint.set()

    else:
        await message.answer(
            'Некорректный запрос. Если вы переслали сообщение, то профиль получателя закрыт, если юзернейм,'
            'то он должен начинаться с @. Если вы хотите написать номер, то он должен начинаться с +')



    await message.answer('Я всё правильно понял?')
    await message.answer(f'Твоя валентинка будет отправлена пользователю {username}')



    keyboard = await is_correct_keyboard(letter)
    await message.answer(text_val, reply_markup=keyboard)



@dp.message_handler(state=states.Letter.correct_val, content_types=['text'])
async def text_val_answer(message: types.Message, state: FSMContext):
    data = await state.get_data()
    text_val = message.text
    await state.update_data(answer2=text_val)
    letter_id = data.get("letter_id")

    # try
    recipient_username = data.get('recipient_username')
    recipient_id = data.get('recipient_id')
    recipient_phone_number = data.get('recipient_phone_number')

    letter = await models.Letter.get(letter_id)

    if recipient_username and recipient_id:
        username = recipient_username
        await letter.update(
            recipient_username=recipient_username,
            recipient_id=recipient_id
        ).apply()
    elif recipient_id:
        username = recipient_id
        await letter.update(
            recipient_id=recipient_id
        ).apply()
    elif recipient_username:
        username = recipient_username
        await letter.update(
            recipient_username=recipient_username
        ).apply()

    elif recipient_phone_number:

        username = recipient_phone_number
        await letter.update(
            recipient_phone_number=recipient_phone_number
        ).apply()
    else:
        print("problem")


    await letter.update(
        type='TEXT',
        text=text_val,
        sender_id=message.from_user.id
    ).apply()



    await state.update_data(letter_id=letter.id)

    await message.answer('Я всё правильно понял?')
    await message.answer(f'Твоя валентинка будет отправлена пользователю {username}')
    await message.answer('Текст валентинки: ')
    keyboard = await is_correct_keyboard(letter)
    await message.answer(text_val, reply_markup=keyboard, parse_mode='HTML')
    await states.Letter.endpoint.set()


@dp.message_handler(state=states.Letter.correct_val, content_types=['photo'])
async def text_val_answer(message: types.Message, state: FSMContext):

    data = await state.get_data()
    username = data.get('answer1')
    text_val = message.photo[-1].file_id
    await state.update_data(answer2=text_val)
    letter_id = data.get("letter_id")

    # try
    recipient_username = data.get('recipient_username')
    recipient_id = data.get('recipient_id')
    recipient_phone_number = data.get('recipient_phone_number')

    letter = await models.Letter.get(letter_id)

    if recipient_username and recipient_id:
        username = recipient_username
        await letter.update(
            recipient_username=recipient_username,
            recipient_id=recipient_id
        ).apply()
    elif recipient_id:
        username = recipient_id
        await letter.update(
            recipient_id=recipient_id
        ).apply()
    elif recipient_username:
        username = recipient_username
        await letter.update(
            recipient_username=recipient_username
        ).apply()

    elif recipient_phone_number:

        username = recipient_phone_number
        await letter.update(
            recipient_phone_number=recipient_phone_number
        ).apply()
    else:
        print("problem")


    await letter.update(
        type='PHOTO',
        text=message.caption,
        file_id=text_val,
        sender_id=message.from_user.id
    ).apply()

    await state.update_data(letter_id=letter.id)
    await message.answer('Я всё правильно понял?')
    await message.answer(f'Твоя валентинка будет отправлена пользователю {username}')
    keyboard = await is_correct_keyboard(letter)
    await message.answer_photo(photo=letter.file_id, caption=letter.text)
    await message.answer('Ваше фото', reply_markup=keyboard)

    await states.Letter.endpoint.set()


@dp.message_handler(state=states.Letter.correct_val, content_types=['video'])
async def text_val_answer(message: types.Message, state: FSMContext):

    text_val = message.video.file_id

    data = await state.get_data()
    await state.update_data(answer2=text_val)
    letter_id = data.get("letter_id")

    # try
    recipient_username = data.get('recipient_username')
    recipient_id = data.get('recipient_id')
    recipient_phone_number = data.get('recipient_phone_number')

    letter = await models.Letter.get(letter_id)

    if recipient_username and recipient_id:
        username = recipient_username
        await letter.update(
            recipient_username=recipient_username,
            recipient_id=recipient_id
        ).apply()
    elif recipient_id:
        username = recipient_id
        await letter.update(
            recipient_id=recipient_id
        ).apply()
    elif recipient_username:
        username = recipient_username
        await letter.update(
            recipient_username=recipient_username
        ).apply()

    elif recipient_phone_number:

        username = recipient_phone_number
        await letter.update(
            recipient_phone_number=recipient_phone_number
        ).apply()
    else:
        print("problem")


    await letter.update(
        type='VIDEO',
        text=message.caption,
        sender_id=message.from_user.id,
        file_id=text_val
    ).apply()

    await state.update_data(letter_id=letter.id)
    await message.answer('Я всё правильно понял?')
    await message.answer(f'Твоя валентинка будет отправлена пользователю {username}')
    keyboard = await is_correct_keyboard(letter)
    await message.answer_video(video=letter.file_id, caption=letter.text)
    await message.answer('Ваше видео', reply_markup=keyboard)

    await states.Letter.endpoint.set()


@dp.message_handler(state=states.Letter.correct_val, content_types=['animation'])
async def text_val_answer(message: types.Message, state: FSMContext):

    text_val = message.animation.file_id

    data = await state.get_data()
    await state.update_data(answer2=text_val)
    letter_id = data.get("letter_id")

    # try
    recipient_username = data.get('recipient_username')
    recipient_id = data.get('recipient_id')
    recipient_phone_number = data.get('recipient_phone_number')

    letter = await models.Letter.get(letter_id)

    if recipient_username and recipient_id:
        username = recipient_username
        await letter.update(
            recipient_username=recipient_username,
            recipient_id=recipient_id
        ).apply()
    elif recipient_id:
        username = recipient_id
        await letter.update(
            recipient_id=recipient_id
        ).apply()
    elif recipient_username:
        username = recipient_username
        await letter.update(
            recipient_username=recipient_username
        ).apply()

    elif recipient_phone_number:

        username = recipient_phone_number
        await letter.update(
            recipient_phone_number=recipient_phone_number
        ).apply()
    else:
        print("problem")


    await letter.update(
        type='GIF',
        sender_id=message.from_user.id,
        file_id=text_val
    ).apply()

    await state.update_data(letter_id=letter.id)
    await message.answer('Я всё правильно понял?')
    await message.answer(f'Твоя валентинка будет отправлена пользователю {username}')
    keyboard = await is_correct_keyboard(letter)
    await message.answer_animation(animation=letter.file_id)
    await message.answer('Ваша гифка', reply_markup=keyboard)

    await states.Letter.endpoint.set()


@dp.message_handler(state=states.Letter.correct_val, content_types=['sticker'])
async def text_val_answer(message: types.Message, state: FSMContext):

    text_val = message.sticker.file_id

    data = await state.get_data()
    await state.update_data(answer2=text_val)
    letter_id = data.get("letter_id")

    # try
    recipient_username = data.get('recipient_username')
    recipient_id = data.get('recipient_id')
    recipient_phone_number = data.get('recipient_phone_number')

    letter = await models.Letter.get(letter_id)

    if recipient_username and recipient_id:
        username = recipient_username
        await letter.update(
            recipient_username=recipient_username,
            recipient_id=recipient_id
        ).apply()
    elif recipient_id:
        username = recipient_id
        await letter.update(
            recipient_id=recipient_id
        ).apply()
    elif recipient_username:
        username = recipient_username
        await letter.update(
            recipient_username=recipient_username
        ).apply()

    elif recipient_phone_number:

        username = recipient_phone_number
        await letter.update(
            recipient_phone_number=recipient_phone_number
        ).apply()
    else:
        print("problem")


    await letter.update(
        type='STICKER',
        sender_id=message.from_user.id,
        file_id=text_val
    ).apply()

    await state.update_data(letter_id=letter.id)
    await message.answer('Я всё правильно понял?')
    await message.answer(f'Твоя валентинка будет отправлена пользователю {username}')
    keyboard = await is_correct_keyboard(letter)
    await message.answer_sticker(sticker=letter.file_id)
    await message.answer('Ваш стикер', reply_markup=keyboard)

    await states.Letter.endpoint.set()


@dp.message_handler(state=states.Letter.correct_val, content_types=['voice'])
async def text_val_answer(message: types.Message, state: FSMContext):

    text_val = message.voice.file_id

    data = await state.get_data()
    await state.update_data(answer2=text_val)
    letter_id = data.get("letter_id")

    # try
    recipient_username = data.get('recipient_username')
    recipient_id = data.get('recipient_id')
    recipient_phone_number = data.get('recipient_phone_number')

    letter = await models.Letter.get(letter_id)

    if recipient_username and recipient_id:
        username = recipient_username
        await letter.update(
            recipient_username=recipient_username,
            recipient_id=recipient_id
        ).apply()
    elif recipient_id:
        username = recipient_id
        await letter.update(
            recipient_id=recipient_id
        ).apply()
    elif recipient_username:
        username = recipient_username
        await letter.update(
            recipient_username=recipient_username
        ).apply()

    elif recipient_phone_number:

        username = recipient_phone_number
        await letter.update(
            recipient_phone_number=recipient_phone_number
        ).apply()
    else:
        print("problem")


    await letter.update(
        type='VOICE',
        sender_id=message.from_user.id,
        file_id=text_val
    ).apply()

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


@dp.message_handler(state=states.Letter.correct_val, content_types=['audio'])
async def text_val_answer(message: types.Message, state: FSMContext):

    text_val = message.audio.file_id

    data = await state.get_data()
    await state.update_data(answer2=text_val)
    letter_id = data.get("letter_id")

    # try
    recipient_username = data.get('recipient_username')
    recipient_id = data.get('recipient_id')
    recipient_phone_number = data.get('recipient_phone_number')

    letter = await models.Letter.get(letter_id)

    if recipient_username and recipient_id:
        username = recipient_username
        await letter.update(
            recipient_username=recipient_username,
            recipient_id=recipient_id
        ).apply()
    elif recipient_id:
        username = recipient_id
        await letter.update(
            recipient_id=recipient_id
        ).apply()
    elif recipient_username:
        username = recipient_username
        await letter.update(
            recipient_username=recipient_username
        ).apply()

    elif recipient_phone_number:

        username = recipient_phone_number
        await letter.update(
            recipient_phone_number=recipient_phone_number
        ).apply()
    else:
        print("problem")


    await letter.update(
        type='AUDIO',
        sender_id=message.from_user.id,
        file_id=text_val
    ).apply()

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


@dp.message_handler(state=states.Letter.correct_val, content_types=['video_note'])
async def text_val_answer(message: types.Message, state: FSMContext):

    text_val = message.video_note.file_id

    data = await state.get_data()
    await state.update_data(answer2=text_val)
    letter_id = data.get("letter_id")

    # try
    recipient_username = data.get('recipient_username')
    recipient_id = data.get('recipient_id')
    recipient_phone_number = data.get('recipient_phone_number')

    letter = await models.Letter.get(letter_id)

    if recipient_username and recipient_id:
        username = recipient_username
        await letter.update(
            recipient_username=recipient_username,
            recipient_id=recipient_id
        ).apply()
    elif recipient_id:
        username = recipient_id
        await letter.update(
            recipient_id=recipient_id
        ).apply()
    elif recipient_username:
        username = recipient_username
        await letter.update(
            recipient_username=recipient_username
        ).apply()

    elif recipient_phone_number:

        username = recipient_phone_number
        await letter.update(
            recipient_phone_number=recipient_phone_number
        ).apply()
    else:
        print("problem")


    await letter.update(
        type='VIDEO_NOTE',
        sender_id=message.from_user.id,
        file_id=text_val
    ).apply()

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
    await bot.send_message(moder_chat_id, 'Юзернейм')
    if letter.recipient_username:
        await bot.send_message(moder_chat_id, letter.recipient_username)
    elif letter.recipient_phone_number:
        await bot.send_message(moder_chat_id, letter.recipient_phone_number)
    else:
        await bot.send_message(moder_chat_id, letter.recipient_id)
    await bot.send_message(moder_chat_id, 'Текст валентинки')
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
