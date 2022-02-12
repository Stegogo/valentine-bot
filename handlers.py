from urllib import request

import aiogram
import requests as requests
from aiogram.dispatcher import FSMContext
from aiogram.types import BotCommandScopeDefault, BotCommandScopeChat, BotCommand, ReplyKeyboardRemove
from aiogram import md
from aiogram.utils.markdown import hide_link
from aiograph import Telegraph
import data
import keyboards
import states
from data import moder_chat_id
from main import bot, dp
from keyboards import menu_cd, is_correct_keyboard, check_markup, reject_keyboard
from aiogram import types, Dispatcher
import postgres
import models

@dp.message_handler(commands=["cancel"], state=states.Letter.add_photo_to_text)
async def cancel(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    letter: models.Letter = state_data.get('letter')

    await message.answer(await get_message_to_answer(letter), parse_mode="HTML")

    letter_preview = await message.answer(letter.text, parse_mode="HTML")
    keyboard = await is_correct_keyboard(letter, letter_preview_id=letter_preview.message_id)
    await message.answer('Я всё правильно понял?', reply_markup=keyboard, parse_mode="HTML")
    await state.reset_state()


@dp.message_handler(commands=["cancel"], state="*")
async def cancel(message: types.Message, state: FSMContext):
    await message.answer("Отмена", reply_markup=ReplyKeyboardRemove())

    await state.reset_state()


@dp.my_chat_member_handler()
async def chat_update(my_chat_member: types.ChatMemberUpdated):
    user = types.User.get_current()
    user_in_DB: models.User = await postgres.get_user_by_tg_id(user.id)
    if user_in_DB:
        if my_chat_member.new_chat_member.status == "kicked":
            text = f'<a href="tg://user?id={str(user_in_DB.tg_id)}">{str(user_in_DB.fullname)}</a> заблокировал бота'
            await bot.send_message(chat_id=243568187, text=text, parse_mode="HTML")
            await user_in_DB.update(is_bot_blocked=True).apply()
        elif my_chat_member.new_chat_member.status == "member":

            text = f'<a href="tg://user?id={str(user_in_DB.tg_id)}">{str(user_in_DB.fullname)}</a> разблокировал бота'
            await bot.send_message(chat_id=243568187, text=text, parse_mode="HTML")
            await user_in_DB.update(is_bot_blocked=False).apply()
        await dashboard()


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    if not await default_check(types.User.get_current()):
        await message.answer_sticker(sticker="CAACAgQAAxkBAAIGXV__bWFhszPnWYSQJvKthQoMiem8AAJrAAPOOQgNWWbqY3aSS9AeBA")
        # Срабатывает, если пользователя нет в дб и добавляет его туда
        await message.answer("Привет! Я бот, который отправляет поздравления другим людям!")
        await postgres.create_user(message.from_user.id)  #
        await dashboard()
    await message.answer(
        'Отправь нам @юзернейм или телефон твоей радости🥰. Можешь также переслать ее сообщение, если ее профиль открыт.')
    await states.Letter.q_username.set()


@dp.message_handler(commands=['new'])
async def new_letter(message: types.Message):
    if await default_check(types.User.get_current()):
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
    if await default_check(types.User.get_current()):
        username = message.text
        letter = models.Letter()
        if message.forward_from:
            letter.recipient_id = message.forward_from.id
            letter.recipient_fullname = message.forward_from.full_name
            if message.forward_from.username:
                letter.recipient_username = message.forward_from.username

        elif username.startswith('@'):
            letter.recipient_username = username[1:]
        elif username.startswith('+'):
            letter.recipient_phone_number = username
        else:
            await message.answer(
                'Некорректный запрос. Если вы переслали сообщение, то профиль получателя закрыт, если юзернейм,'
                'то он должен начинаться с @. Если вы хотите написать номер, то он должен начинаться с +')
            return
        await message.answer('Супер! Мы нашли его! Теперь мы ждём текст твоей валентинки🧐')
        await states.Letter.q_text_val.set()
        await state.update_data(letter=letter)

async def get_message_to_answer(letter):
    text = 'Твоя валентинка будет отправлена пользователю '
    if letter.recipient_id != None:
        if letter.recipient_fullname:
            text += f'<a href="tg://user?id={str(letter.recipient_id)}">{str(letter.recipient_fullname)}</a>'
        else:
            text = f'Твоя валентинка будет отправлена <a href="tg://user?id={str(letter.recipient_id)}"> этому пользователю</a>'
    elif letter.recipient_username != None:
        text += f"@{letter.recipient_username}"
    elif letter.recipient_phone_number != None:
        text += f" с номером {letter.recipient_phone_number}"

    return text


async def get_admin_message_text(letter):
    circles = ""
    if letter.status == "CHECKING":
        circles = "🔴🔴🔴"
    elif letter.status == "REJECTED":
        circles = "🔵🔵🔵"
    elif letter.status == "APPROVED":
        circles = "🟡🟡🟡"
    elif letter.status == "ERROR":
        circles = "❌❌❌"
    elif letter.status == "DELIVERED":
        circles = "🟢🟢🟢"

    text_to_admins = circles + f"\nНовая валентинка\n\nПолучатель: "
    if letter.recipient_username != None:
        text_to_admins += f"@{letter.recipient_username}"

    elif letter.recipient_id != None:
        if letter.recipient_fullname:
            text_to_admins += f'<a href="tg://user?id={str(letter.recipient_id)}">{str(letter.recipient_fullname)}</a>'
        else:
            text_to_admins += f'<a href="tg://user?id={str(letter.recipient_id)}">Этот человек</a>'
        if letter.recipient_phone_number != None:
            text_to_admins += f"\n(<code>{letter.recipient_phone_number}</code>)\nСодержание:"
        else:
            text_to_admins += f"\nСодержание:"
    elif letter.recipient_phone_number != None:
        text_to_admins += f"<code>{letter.recipient_phone_number}</code>\nСодержание:"

    return text_to_admins


@dp.message_handler(state=states.Letter.q_text_val, content_types=['text'])
async def text_val_answer(message: types.Message, state: FSMContext):
    if await default_check(types.User.get_current()):
        data = await state.get_data()
        letter: models.Letter = data.get('letter')
        text_val = message.html_text
        letter.text = text_val
        letter.type = "TEXT"
        letter.sender_message_id = message.message_id
        letter.link_preview = True
        letter.sender_id = message.from_user.id
        letter.status = "CREATING"
        if letter.id:
            await letter.update(text = text_val, type = "TEXT", sender_message_id = message.message_id, link_preview = True,sender_id = message.from_user.id, status = "CREATING").apply()
        else:
            letter = await letter.create()
            await dashboard()
        await message.answer(await get_message_to_answer(letter), parse_mode="HTML")

        letter_preview = await message.answer(text_val, parse_mode="HTML")
        keyboard = await is_correct_keyboard(letter, letter_preview.message_id)
        await message.answer('Я всё правильно понял?', reply_markup=keyboard, parse_mode="HTML")
        await state.reset_state()


@dp.message_handler(state=states.Letter.q_text_val, content_types=['photo'])
async def text_val_answer(message: types.Message, state: FSMContext):
    if await default_check(types.User.get_current()):
        data = await state.get_data()
        letter: models.Letter = data.get('letter')
        text_val = message.photo[-1].file_id
        if message.caption:
            letter.text = message.html_text
        else:
            letter.text = None
        letter.type = "PHOTO"
        letter.sender_message_id = message.message_id
        letter.link_preview = True
        letter.sender_id = message.from_user.id
        letter.file_id_bot = text_val
        letter.status = "CREATING"
        if letter.id:
            await letter.update(text = letter.text, type="PHOTO", sender_message_id=message.message_id, link_preview=True,
                                sender_id=message.from_user.id, file_id_bot = text_val, status = "CREATING").apply()
        else:
            letter = await letter.create()
            await dashboard()
        await message.answer(await get_message_to_answer(letter), parse_mode="HTML")

        letter_preview = await message.answer_photo(photo=letter.file_id_bot, caption=letter.text, parse_mode="HTML")
        keyboard = await is_correct_keyboard(letter, letter_preview.message_id)
        await message.answer('Я всё правильно понял?', reply_markup=keyboard, parse_mode="HTML")
        await state.reset_state()




@dp.message_handler(state=states.Letter.q_text_val, content_types=['video'])
async def text_val_answer(message: types.Message, state: FSMContext):
    if await default_check(types.User.get_current()):
        data = await state.get_data()
        letter: models.Letter = data.get('letter')
        text_val = message.video.file_id
        if message.caption:
            letter.text = message.html_text
        else:
            letter.text = None
        letter.type = "VIDEO"
        letter.sender_message_id = message.message_id
        letter.link_preview = True
        letter.sender_id = message.from_user.id
        letter.file_id_bot = text_val
        letter.status = "CREATING"
        if letter.id:
            await letter.update(text = letter.text, type="VIDEO", sender_message_id=message.message_id, link_preview=True,
                                sender_id=message.from_user.id, file_id_bot=text_val, status = "CREATING").apply()
        else:
            letter = await letter.create()
            await dashboard()
        await message.answer(await get_message_to_answer(letter), parse_mode="HTML")

        letter_preview = await message.answer_video(video=letter.file_id_bot, caption=letter.text, parse_mode="HTML")
        keyboard = await is_correct_keyboard(letter, letter_preview.message_id)
        await message.answer('Я всё правильно понял?', reply_markup=keyboard, parse_mode="HTML")
        await state.reset_state()



@dp.message_handler(state=states.Letter.q_text_val, content_types=['animation'])
async def text_val_answer(message: types.Message, state: FSMContext):
    if await default_check(types.User.get_current()):
        data = await state.get_data()
        letter: models.Letter = data.get('letter')
        text_val = message.animation.file_id
        if message.caption:
            letter.text = message.html_text
        else:
            letter.text = None

        letter.type = "ANIMATION"
        letter.sender_message_id = message.message_id
        letter.link_preview = True
        letter.sender_id = message.from_user.id
        letter.file_id_bot = text_val
        letter.status = "CREATING"
        if letter.id:
            await letter.update(text = letter.text, type="ANIMATION", sender_message_id=message.message_id, link_preview=True,
                                sender_id=message.from_user.id, file_id_bot=text_val, status = "CREATING").apply()
        else:
            letter = await letter.create()
            await dashboard()
        await message.answer(await get_message_to_answer(letter), parse_mode="HTML")

        letter_preview = await message.answer_animation(animation=letter.file_id_bot, caption=letter.text, parse_mode="HTML")
        keyboard = await is_correct_keyboard(letter, letter_preview.message_id)
        await message.answer('Я всё правильно понял?', reply_markup=keyboard, parse_mode="HTML")
        await state.reset_state()


@dp.message_handler(state=states.Letter.q_text_val, content_types=['sticker'])
async def text_val_answer(message: types.Message, state: FSMContext):
    if await default_check(types.User.get_current()):
        data = await state.get_data()
        letter: models.Letter = data.get('letter')
        text_val = message.sticker.file_id
        letter.type = "STICKER"
        letter.sender_message_id = message.message_id
        letter.link_preview = True
        letter.sender_id = message.from_user.id
        letter.file_id_bot = text_val
        letter.status = "CREATING"
        if letter.id:
            await letter.update(type="STICKER", sender_message_id=message.message_id, link_preview=True,
                                sender_id=message.from_user.id, file_id_bot=text_val, text=None, status = "CREATING").apply()
        else:
            letter = await letter.create()
            await dashboard()
        await message.answer(await get_message_to_answer(letter), parse_mode="HTML")

        letter_preview = await message.answer_sticker(sticker=letter.file_id_bot)
        keyboard = await is_correct_keyboard(letter, letter_preview.message_id)
        await message.answer('Я всё правильно понял?', reply_markup=keyboard, parse_mode="HTML")
        await state.reset_state()



@dp.message_handler(state=states.Letter.q_text_val, content_types=['voice'])
async def text_val_answer(message: types.Message, state: FSMContext):
    if await default_check(types.User.get_current()):
        data = await state.get_data()
        letter: models.Letter = data.get('letter')
        text_val = message.voice.file_id
        letter.type = "VOICE"
        letter.sender_message_id = message.message_id
        letter.link_preview = True
        letter.sender_id = message.from_user.id
        letter.file_id_bot = text_val
        letter.status = "CREATING"
        if letter.id:
            await letter.update(type="VOICE", sender_message_id=message.message_id, link_preview=True,
                                sender_id=message.from_user.id, file_id_bot=text_val, text=None, status = "CREATING").apply()
        else:
            letter = await letter.create()
            await dashboard()
        await message.answer(await get_message_to_answer(letter), parse_mode="HTML")

        letter_preview = await message.answer_voice(voice=letter.file_id_bot)
        keyboard = await is_correct_keyboard(letter, letter_preview.message_id)
        await message.answer('Я всё правильно понял?', reply_markup=keyboard, parse_mode="HTML")
        await state.reset_state()



@dp.message_handler(state=states.Letter.q_text_val, content_types=['audio'])
async def text_val_answer(message: types.Message, state: FSMContext):
    if await default_check(types.User.get_current()):
        data = await state.get_data()
        letter: models.Letter = data.get('letter')
        text_val = message.audio.file_id
        letter.type = "AUDIO"
        letter.sender_message_id = message.message_id
        letter.link_preview = True
        letter.sender_id = message.from_user.id
        letter.file_id_bot = text_val
        letter.status = "CREATING"
        if letter.id:
            await letter.update(type="AUDIO", sender_message_id=message.message_id, link_preview=True,
                                sender_id=message.from_user.id, file_id_bot=text_val, text=None, status = "CREATING").apply()
        else:
            letter = await letter.create()
            await dashboard()
        await message.answer(await get_message_to_answer(letter), parse_mode="HTML")

        letter_preview = await message.answer_audio(audio=letter.file_id_bot)
        keyboard = await is_correct_keyboard(letter, letter_preview.message_id)
        await message.answer('Я всё правильно понял?', reply_markup=keyboard, parse_mode="HTML")
        await state.reset_state()


@dp.message_handler(state=states.Letter.q_text_val, content_types=['video_note'])
async def text_val_answer(message: types.Message, state: FSMContext):
    if await default_check(types.User.get_current()):
        data = await state.get_data()
        letter: models.Letter = data.get('letter')
        text_val = message.video_note.file_id
        letter.type = "VIDEO_NOTE"
        letter.sender_message_id = message.message_id
        letter.link_preview = True
        letter.sender_id = message.from_user.id
        letter.file_id_bot = text_val
        letter.status = "CREATING"
        if letter.id:
            await letter.update(type="VIDEO_NOTE", sender_message_id=message.message_id, link_preview=True,
                                sender_id=message.from_user.id, file_id_bot=text_val, text=None, status = "CREATING").apply()
        else:
            letter = await letter.create()
            await dashboard()
        await message.answer(await get_message_to_answer(letter), parse_mode="HTML")

        letter_preview = await message.answer_video_note(video_note=letter.file_id_bot)
        keyboard = await is_correct_keyboard(letter, letter_preview.message_id)
        await message.answer('Я всё правильно понял?', reply_markup=keyboard, parse_mode="HTML")
        await state.reset_state()


@dp.message_handler(state=states.Letter.correct_username)
async def text_val_answer1(message: types.Message, state: FSMContext):
    if await default_check(types.User.get_current()):
        username = message.text
        data = await state.get_data()
        letter = data.get('letter')
        recipient_id=None
        recipient_username = None
        recipient_phone_number=None
        if message.forward_from:
            recipient_id = message.forward_from.id
            if message.forward_from.username:
                recipient_username = message.forward_from.username
        elif username.startswith('@'):
            recipient_username = username[1:]
        elif username.startswith('+'):
            recipient_phone_number = username
        else:
            await message.answer(
                'Некорректный запрос. Если вы переслали сообщение, то профиль получателя закрыт, если юзернейм,'
                'то он должен начинаться с @. Если вы хотите написать номер, то он должен начинаться с +')
            return
        letter.recipient_id=recipient_id
        letter.recipient_username = recipient_username
        letter.recipient_phone_number = recipient_phone_number
        await letter.update(recipient_id=recipient_id, recipient_username = recipient_username, recipient_phone_number = recipient_phone_number).apply()
        await message.answer(await get_message_to_answer(letter), parse_mode="HTML")

        letter_preview = await send_letter(letter, chat_id=message.chat.id)
        keyboard = await is_correct_keyboard(letter, letter_preview.message_id)
        await message.answer('Я всё правильно понял?', reply_markup=keyboard, parse_mode="HTML")
        await state.reset_state()




@dp.message_handler(state=states.Letter.add_photo_to_text, content_types=['photo', 'animation'])
async def add_photo_to_text_get_photo(message: types.Message, state: FSMContext):
    if await default_check(types.User.get_current()):

        if message.content_type == "photo":
            file_id = message.photo[-1].file_id
        else:
            file_id = message.animation.file_id
        answer = requests.get(f"https://api.telegram.org/bot{data.token}/getFile?file_id={file_id}")
        json = answer.json()
        result = json["result"]
        file_url = f"https://api.telegram.org/file/bot{data.token}/{result['file_path']}"
        telegraph = Telegraph()
        link = await telegraph.upload_from_url(url=file_url)
        await telegraph.close()
        state_data = await state.get_data()
        letter: models.Letter = state_data.get('letter')
        old_text = letter.text
        letter.text = hide_link(link)+old_text
        letter.file_id_bot = str(len(hide_link(link)))
        letter.link_preview = True
        await letter.update(text = hide_link(link)+old_text , link_preview = True, file_id_bot = str(len(hide_link(link)))).apply()
        await message.answer(await get_message_to_answer(letter), parse_mode="HTML")

        letter_preview = await message.answer(letter.text, parse_mode="HTML")
        keyboard = await is_correct_keyboard(letter, letter_preview_id=letter_preview.message_id)
        await message.answer('Я всё правильно понял?', reply_markup=keyboard, parse_mode="HTML")
        await state.reset_state()

@dp.message_handler(state=states.Letter.add_photo_to_text, content_types=['text', 'video'])
async def add_photo_to_text_not_photo(message: types.Message, state: FSMContext):
    if await default_check(types.User.get_current()):
        await message.answer("Пришли мне фото, которое хочешь прикрепить. Чтоб вернуться назад - нажми /cancel")



async def process_callback_button1(callback_query: types.CallbackQuery, id,**kwargs):
    if await default_check(types.User.get_current()):
        await bot.answer_callback_query(callback_query.id)
        await callback_query.message.edit_text('Отправь исправленный юзернейм')
        await states.Letter.correct_username.set()
        state = Dispatcher.get_current().current_state()
        letter = await postgres.get_letter(int(id))
        await state.update_data(letter=letter)

async def process_callback_button2(callback_query: types.CallbackQuery, id, **kwargs):
    if await default_check(types.User.get_current()):
        await bot.answer_callback_query(callback_query.id)
        await callback_query.message.edit_text('Отправь новую валентинку')
        await states.Letter.q_text_val.set()
        state = Dispatcher.get_current().current_state()
        letter = await postgres.get_letter(int(id))
        await state.update_data(letter=letter)

async def add_photo_to_text(callback_query: types.CallbackQuery, id, extra_data, **kwargs):
    if await default_check(types.User.get_current()):
        await bot.answer_callback_query(callback_query.id)
        await callback_query.message.edit_text('Пришли фото, которое хочешь прикрепить')
        await states.Letter.add_photo_to_text.set()
        state = Dispatcher.get_current().current_state()
        letter = await postgres.get_letter(int(id))
        await state.update_data(letter=letter)


async def remove_photo_from_text(callback_query: types.CallbackQuery, id, extra_data, **kwargs):
    if await default_check(types.User.get_current()):
        await bot.answer_callback_query(callback_query.id)
        letter = await postgres.get_letter(int(id))
        if letter.file_id_bot:
            old_text = letter.text
            letter.text = old_text[int(letter.file_id_bot):]
            await letter.update(file_id_bot = None, text = old_text[int(letter.file_id_bot):]).apply()

            await callback_query.message.edit_reply_markup(await is_correct_keyboard(letter, extra_data))
            await bot.edit_message_text(text=letter.text, chat_id=callback_query.message.chat.id, message_id=int(extra_data), parse_mode="HTML")




async def process_callback_button3(callback_query: types.CallbackQuery, id, **kwargs):
    if await default_check(types.User.get_current()):
        await bot.answer_callback_query(callback_query.id)

        #await callback_query.message.edit_text('Отправили! Чтобы прислать мне ещё одну валентинку нажми на /new)')
        letter = await postgres.get_letter(int(id))

        letter.status = "CHECKING"

        try:
            await callback_query.message.delete()
        except:
            await callback_query.message.edit_text("Отправляю...")
            await callback_query.message.delete_reply_markup()

        admin_mess_1 = await bot.send_message(chat_id=data.moder_chat_id, text=await get_admin_message_text(letter), parse_mode="HTML")
        await send_letter(letter, chat_id=data.moder_chat_id)
        letter.admin_message_id = admin_mess_1.message_id
        await letter.update(admin_message_id = admin_mess_1.message_id, status = "CHECKING").apply()
        await dashboard()
        markup = await keyboards.check_markup(letter=letter)
        text = "Что сделать?"
        if letter.recipient_username == None and letter.recipient_id != None:
            userbot = await postgres.get_user_by_tg_id(data.userbot_id)
            text += f"\nЧтоб отправить сообщение этому юзеру, {userbot.fullname} должен вручную начать диалог. Когда чат будет создан, {userbot.fullname} должен нажать кнопку ниже"
        await bot.send_message(chat_id=data.moder_chat_id, text=text, reply_markup=markup)
        await callback_query.message.answer(
            "Твое сообщение отправлено модераторам для проверки. Как только оно будет доставлено получателю, мы уведомим тебя. Чтобы прислать мне ещё одну валентинку нажми на /new, чтоб посмотреть статус твоих валентинок, нажми /my_letters")






async def disable_preview(call: types.CallbackQuery, id, extra_data, **kwargs):
    if await default_check(types.User.get_current()):

        letter= await postgres.get_letter(int(id))

        letter.link_preview = False
        await letter.update(link_preview = False).apply()
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=extra_data, text=letter.text, disable_web_page_preview=True, parse_mode="HTML")
        markup = await keyboards.is_correct_keyboard(letter, extra_data)
        await bot.answer_callback_query(call.id)
        await call.message.edit_reply_markup(reply_markup=markup)



async def enable_preview(call: types.CallbackQuery,id , extra_data, **kwargs):
    if await default_check(types.User.get_current()):
        letter = await postgres.get_letter(int(id))

        letter.link_preview = True
        await letter.update(link_preview=True).apply()
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=extra_data, text=letter.text,
                                    disable_web_page_preview=False, parse_mode="HTML")
        markup = await keyboards.is_correct_keyboard(letter, extra_data)
        await bot.answer_callback_query(call.id)
        await call.message.edit_reply_markup(reply_markup=markup)


async def add_contact(call: types.CallbackQuery, id, **kwargs):
    if await default_check(types.User.get_current(), admin=True):

        letter = await postgres.get_letter(int(id))
        keyboard = await keyboards.add_contact_keyboard(letter)
        await call.message.edit_text("Пришли айди или юзернейм получателя", reply_markup=keyboard)
        await states.Letter.add_receiver_contact.set()
        state = Dispatcher.get_current().current_state()
        await bot.answer_callback_query(call.id)
        await state.update_data(letter_id=id)


@dp.message_handler(state=states.Letter.add_receiver_contact)
async def add_receiver_contact(message: types.Message, state: FSMContext):
    if await default_check(types.User.get_current(), admin=True):
        state_data = await state.get_data()
        letter: models.Letter = await postgres.get_letter(int(state_data.get("letter_id")))
        if message.text.startswith("@"):
            letter.recipient_username = message.text[1:]
            await letter.update(recipient_username = message.text[1:]).apply()
        elif message.text.isdigit():
            letter.recipient_id = int(message.text)
            await letter.update(recipient_id = int(message.text)).apply()
        else:
            await message.answer("Ошибка. Пришли мне юзернейм или айди получателя", reply=message.message_id)
            return


        await bot.edit_message_text(chat_id=data.moder_chat_id, message_id=int(letter.admin_message_id), text=await get_admin_message_text(letter), parse_mode="HTML")
        if message.reply_to_message != None:
            keyboard = await keyboards.check_markup(letter)
            await message.reply_to_message.edit_text("Что сделать?", reply_markup=keyboard)
        await message.answer(text="Принято", reply=message.message_id)

        await state.reset_state()


@dp.message_handler(state=states.Letter.reject_reason)
async def reject_text(message: types.Message, state: FSMContext):
    if await default_check(types.User.get_current(), admin=True):
        state_data = await state.get_data()
        letter: models.Letter = await postgres.get_letter(int(state_data.get("letter_id")))
        letter.reject_reason = message.text
        letter.status = "REJECTED"
        await letter.update(reject_reason=message.text, status="REJECTED").apply()
        await dashboard()
        await bot.send_message(chat_id=letter.sender_id, text=f"К сожалению, модератор не принял твою валентинку.\n"
                                                              f"Причина: {letter.reject_reason}",
                               reply_to_message_id=letter.sender_message_id)

        await bot.edit_message_text(chat_id=data.moder_chat_id, message_id=int(letter.admin_message_id), text=await get_admin_message_text(letter))
        if message.reply_to_message != None:
            await message.reply_to_message.edit_text("Валентинка отклонена")
        await message.answer(text="Отправлено", reply=message.message_id)

        await state.reset_state()


async def initialisate_chat_with_user(call: types.CallbackQuery, id, **kwargs):
    if await default_check(types.User.get_current(), admin=True):
        await bot.answer_callback_query(call.id)
        if types.User.get_current().id == data.userbot_id:

            letter= await postgres.get_letter(int(id))
            markup = await keyboards.delivery_confirm_markup(letter=letter)
            await call.message.edit_text(text="Ты точно начал диалог?\nЕсли нет, то сообщение не сможет отправиться",
                                         reply_markup=markup)
        else:
            await bot.answer_callback_query(callback_query_id=call.id, text="Эту кнопку должен нажать акк юзербота",
                                            show_alert=True)


async def reject_letter(call: types.CallbackQuery, id, **kwargs):
    if await default_check(types.User.get_current(), admin=True):
        await bot.answer_callback_query(call.id)
        letter = await postgres.get_letter(int(id))
        keyboard = await reject_keyboard(letter=letter)
        await call.message.edit_text("Напиши причину отказа", reply_markup=keyboard)

        await states.Letter.reject_reason.set()
        state = Dispatcher.get_current().current_state()
        await state.update_data(letter_id=id)

async def approve_letter(call: types.CallbackQuery, id, extra_data, **kwargs):
    if await default_check(types.User.get_current(), admin=True):
        await bot.answer_callback_query(call.id)
        if int(extra_data) == 1 and types.User.get_current().id == data.userbot_id or int(extra_data) == 0:

            await call.message.edit_text("Валентинка принята")
            letter: models.Letter = await postgres.get_letter(int(id))

            letter.status = "APPROVED"
            await letter.update(status="APPROVED").apply()
            await dashboard()
            if letter.type == "TEXT":
                await bot.send_message(chat_id=data.userbot_id, text=f"/#l:{letter.id}")
            else:
                file = await send_letter(letter=letter, chat_id=data.userbot_id)
                await bot.send_message(chat_id=data.userbot_id, text=f"/#l:{letter.id}",
                                       reply_to_message_id=file.message_id)

            await bot.edit_message_text(chat_id=data.moder_chat_id, message_id=int(letter.admin_message_id),
                                        text=await get_admin_message_text(letter), parse_mode="HTML")
        else:
            await bot.answer_callback_query(callback_query_id=call.id, text="Эту кнопку должен нажать акк юзербота",
                                            show_alert=True)

#@dp.message_handler(lambda message: message.chat_id == data.moder_chat_id, commands=["add_admin"], chat_type=types.ChatType.GROUP)
@dp.message_handler(lambda message: message.chat.id == data.moder_chat_id, commands=["add_admin"])
async def add_admin(mess: types.Message):
    if await default_check(types.User.get_current()):
        message_array = mess.text.split(" ")
        admin_contact = message_array[-1]
        if admin_contact.startswith("@"):
            user_in_db = await postgres.get_user_by_username(admin_contact[1:])
            if user_in_db:
                if user_in_db.is_admin:
                    await mess.answer(f"{admin_contact} и так админ", reply=mess.message_id)
                else:
                    await user_in_db.update(is_admin=True).apply()
                    await mess.answer(f"{admin_contact} назначен админом", reply=mess.message_id)
                    await set_personal_bot_commands(user_in_db.id)
                    await dashboard()
            else:
                await mess.answer(f"Не нашел {admin_contact} в базе", reply=mess.message_id)

        elif admin_contact.isdigit():
            user_in_db = await postgres.get_user_by_tg_id(int(admin_contact))
            if user_in_db:
                if user_in_db.is_admin:
                    await mess.answer(f'<a href="tg://user?id=' + str(
                        user_in_db.tg_id) + '">' + user_in_db.fullname + '</a> и так админ', parse_mode="HTML", reply=mess.message_id)
                else:
                    await user_in_db.update(is_admin=True).apply()
                    await mess.answer(f'<a href="tg://user?id=' + str(
                            user_in_db.tg_id) + '">' + user_in_db.fullname + '</a> назначен админом', parse_mode="HTML", reply=mess.message_id)
                    await set_personal_bot_commands(user_in_db.id)
                    await dashboard()
            else:
                await mess.answer("Не нашел такого человека в базе", reply=mess.message_id)
        else:
            await mess.answer("Формат команды <code>/add_admin id_or_username</code>", reply=mess.message_id, parse_mode="HTML")

@dp.message_handler(lambda message: message.chat.id == data.moder_chat_id, commands=["del_admin"])
async def del_admin(mess: types.Message):
    if await default_check(types.User.get_current(), admin=True):
        message_array = mess.text.split(" ")
        admin_contact = message_array[-1]
        if admin_contact.startswith("@"):
            user_in_db = await postgres.get_user_by_username(admin_contact[1:])
            if user_in_db:
                if not user_in_db.is_admin:
                    await mess.answer(f"{admin_contact} и так не админ", reply=mess.message_id)
                else:
                    await user_in_db.update(is_admin=False).apply()
                    await mess.answer(f"{admin_contact} больше не админ", reply=mess.message_id)
                    await set_personal_bot_commands(user_in_db.id)
                    await dashboard()
            else:
                await mess.answer(f"Не нашел {admin_contact} в базе", reply=mess.message_id)

        elif admin_contact.isdigit():
            user_in_db = await postgres.get_user_by_tg_id(int(admin_contact))
            if user_in_db:
                if not user_in_db.is_admin:
                    await mess.answer(f'<a href="tg://user?id=' + str(
                        user_in_db.tg_id) + '">' + user_in_db.fullname + '</a> и так не админ', parse_mode="HTML", reply=mess.message_id)
                else:
                    await user_in_db.update(is_admin=False).apply()
                    await mess.answer(f'<a href="tg://user?id=' + str(
                            user_in_db.tg_id) + '">' + user_in_db.fullname + '</a> больше не админ', parse_mode="HTML", reply=mess.message_id)
                    await set_personal_bot_commands(user_in_db.id)
                    await dashboard()
            else:
                await mess.answer("Не нашел такого человека в базе", reply=mess.message_id)
        else:
            await mess.answer("Формат команды <code>/del_admin id_or_username</code>", reply=mess.message_id, parse_mode="HTML")


async def admin_menu(call: types.CallbackQuery, id, **kwargs):
    if await default_check(types.User.get_current(), admin=True):
        await bot.answer_callback_query(call.id)
        letter = await postgres.get_letter(int(id))
        keyboard = await check_markup(letter)
        await call.message.edit_text(text="Что сделать?", reply_markup=keyboard)


@dp.callback_query_handler(menu_cd.filter(), state='*')
async def navigate(call: types.CallbackQuery, callback_data: dict):
    current_level = callback_data.get('level')
    id = callback_data.get('id')
    extra_data = callback_data.get('extra_data')
    levels = {
        '1': process_callback_button1,
        '2': process_callback_button2,
        '3': process_callback_button3,
        '4': add_contact,
        '5': initialisate_chat_with_user,
        '6': reject_letter,
        '7': admin_menu,
        '8': approve_letter,
        '9': add_photo_to_text,
        '10': remove_photo_from_text,
        '11': disable_preview,
        '12': enable_preview,


    }

    current_level_function = levels[current_level]

    await current_level_function(
        call, id=id, extra_data=extra_data
    )

async def default_check(user, admin=False):
    user_in_DB: models.User = await postgres.get_user_by_tg_id(user.id)
    if user_in_DB:
        if not user_in_DB.is_bot_blocked:
            if admin:
                if user_in_DB.is_admin:
                    return True
                else:
                    return False
            else:
                return True
        else:
            return False
    return False


@dp.message_handler(lambda msg: msg.from_user.id == data.userbot_id)
async def userbot_connect(message: types.Message):
    if await default_check(types.User.get_current(), admin=True):
        if message.text.startswith("/#"):
            message_dict = message.text[2:].split(":")
            if message_dict[0] == "ls":
                # successfull delivery
                letter = await postgres.get_letter(int(message_dict[1]))

                letter.status = "DELIVERED"
                await letter.update(status="DELIVERED").apply()

                await bot.send_message(chat_id=letter.sender_id,
                                       text=f"Твоя валентинка успешно доставлена получателю",
                                       reply_to_message_id=letter.sender_message_id)

                await bot.edit_message_text(chat_id=moder_chat_id, message_id=int(letter.admin_message_id),
                                            text=await get_admin_message_text(letter), parse_mode="HTML")
            elif message_dict[0] == "le":
                # error delivery
                letter = await postgres.get_letter(int(message_dict[1]))

                letter.status = "ERROR"
                await letter.update(status="ERROR").apply()

                await bot.send_message(chat_id=letter.sender_id,
                                       text=f"К сожалению во время отправки твоей валентинки возникла ошибки, попробуй еще раз",
                                       reply_to_message_id=letter.sender_message_id)

                await bot.edit_message_text(chat_id=data.moder_chat_id, message_id=int(letter.admin_message_id),
                                            text=await get_admin_message_text(letter), parse_mode="HTML")
            elif message_dict[0] == "a":
                answer = await postgres.get_answer(int(message_dict[1]))

                try:
                    if answer.type != "TEXT" and message.reply_to_message != None:
                        answer.file_id_bot = await postgres.get_file_id(answer, message.reply_to_message)
                    await bot.send_message(chat_id=answer.recipient_id, text=f"Тебе прислали ответ!")
                    mess_id = await send_answer(answer=answer)
                    if mess_id == "error":
                        answer.status = "ERROR"
                        await answer.update(status="ERROR", file_id_bot=answer.file_id_bot).apply()
                        await bot.send_message(chat_id=data.userbot_id, text=f"/#ae:{answer.id}")
                    else:
                        answer.status = "DELIVERED"
                        answer.recipient_message_id = mess_id.message_id
                        await answer.update(status="DELIVERED", file_id_bot=answer.file_id_bot,
                                        recipient_message_id=answer.recipient_message_id).apply()
                        await bot.send_message(chat_id=data.userbot_id, text=f"/#as:{answer.id}")
                except:

                    answer.status = "ERROR"
                    await answer.update(status="ERROR").apply()
                    await bot.send_message(chat_id=data.userbot_id, text=f"/#ae:{answer.id}")
            elif message_dict[0] == "ae":
                # error delivery
                answer = await postgres.get_answer(int(message_dict[1]))
                await bot.send_message(chat_id=answer.sender_id,
                                       text=f"Ответ не доставлен, скорее всего собеседник заблокировал меня",
                                       reply_to_message_id=answer.sender_message_id)
            elif message_dict[0] == "as":
                # successfull delivery
                answer = await postgres.get_answer(int(message_dict[1]))
                await bot.send_message(chat_id=answer.sender_id, text=f"Ответ доставлен",
                                       reply_to_message_id=answer.sender_message_id)
            await dashboard()

async def set_personal_bot_commands(user_id):
    user = await postgres.get_user(user_id)
    if user and user.is_admin:
        commands = [BotCommand(command="add_user", description="Добавить админа"),
                    BotCommand(command="del_user", description="Удалить админа"),
                    BotCommand(command="admins", description="Список админов"),
                    BotCommand(command="new", description="Создать валентинку"),
                ]
    else:
        commands = [BotCommand(command="new", description="Создать валентинку"),

                            ]
    await bot.set_my_commands(commands=commands, scope=BotCommandScopeChat(user.tg_id))

async def set_bot_commands():
    commands_default = [BotCommand(command="new", description="Создать валентинку"),

                ]
    commands_admin_chat = [BotCommand(command="add_admin", description="Добавить админа"),
                    BotCommand(command="del_admin", description="Удалить админа"),
                    BotCommand(command="new", description="Создать валентинку"),

                        ]
    await bot.set_my_commands(commands=commands_default, scope=BotCommandScopeDefault())
    await bot.set_my_commands(commands=commands_admin_chat, scope=BotCommandScopeChat(moder_chat_id))

async def dashboard():
    users_size = await postgres.count_users()
    bot_blocked_users = await postgres.count_bot_blocked_users()
    blocked_by_bot_users = await postgres.count_blocked_by_bot_users()
    admin_users = await postgres.count_admin_users()
    letters_size = await postgres.count_letters()
    answers_size = await postgres.count_answers()
    delivered_letters = await postgres.count_delivered_letters()
    approved_letters = await postgres.count_approved_letters()
    error_letters = await postgres.count_error_letters()
    creating_letters = await postgres.count_creating_letters()
    checking_letters = await postgres.count_checking_letters()
    rejected_letters = await postgres.count_rejected_letters()
    sending_answers = await postgres.count_sending_answers()
    error_answers = await postgres.count_error_answers()
    delivered_answers = await postgres.count_delivered_answers()
    text=f"Людей в базе: {users_size}\nЗаблокировали бота: {bot_blocked_users}\nЗаблокированы ботом: {blocked_by_bot_users}\nАдмины: {admin_users}\n\n" \
         f"Валентинок в базе: {letters_size}\nУспешно доставлено: {delivered_letters}\nНа проверке: {checking_letters}\nВ процессе создания: {creating_letters}\n" \
         f"Ошибка доставки: {error_letters}\nОтклонено: {rejected_letters}\nПроверено, но не доставлено: {approved_letters}\n\n" \
         f"Ответов в базе: {answers_size}\nУспешно доставлено: {delivered_answers}\nОшибка доставки: {error_answers}\nДоставляется: {sending_answers}"
    try:
        await bot.edit_message_text(chat_id=data.moder_chat_id, message_id=data.dashboard_message_id, text=text)
    except:
        mess =await bot.send_message(chat_id=data.moder_chat_id, text=text)
        with open("data.py", 'a') as f:
            f.write(f'\ndashboard_message_id = {mess.message_id}')
            f.close()


async def send_letter(letter, chat_id):

    message = None
    if letter.type == "TEXT":
        message = await bot.send_message(chat_id=chat_id, text=letter.text, parse_mode="HTML")
    elif letter.type == "STICKER":
        message = await bot.send_sticker(chat_id=chat_id, sticker=letter.file_id_bot)
    elif letter.type == "PHOTO":
        message = await bot.send_photo(chat_id=chat_id, photo=letter.file_id_bot, caption=letter.text, parse_mode="HTML")
    elif letter.type == "VIDEO":
        message = await bot.send_video(chat_id=chat_id, video=letter.file_id_bot, caption=letter.text, parse_mode="HTML")
    elif letter.type == "VOICE":
        message = await bot.send_voice(chat_id=chat_id, voice=letter.file_id_bot)
    elif letter.type == "VIDEO_NOTE":
        message = await bot.send_video_note(chat_id=chat_id, video_note=letter.file_id_bot)
    elif letter.type == "ANIMATION":
        message = await bot.send_animation(chat_id=chat_id, animation=letter.file_id_bot)
    elif letter.type == "AUDIO":
        message = await bot.send_audio(chat_id=chat_id, audio=letter.file_id_bot)
    return message

async def send_answer(answer, chat_id = None, reply = True):

    try:
        if chat_id == None:
            chat_id = answer.recipient_id
        if not reply:
            answer.to_message_recipient = None
        message = None
        if answer.type == "TEXT":
            message = await bot.send_message(chat_id=chat_id, text=answer.text, reply_to_message_id=answer.to_message_recipient)
        elif answer.type == "STICKER":
            message = await bot.send_sticker(chat_id=chat_id, sticker=answer.file_id_bot, reply_to_message_id=answer.to_message_recipient)
        elif answer.type == "PHOTO":
            message = await bot.send_photo(chat_id=chat_id, photo=answer.file_id_bot, caption=answer.text, reply_to_message_id=answer.to_message_recipient)
        elif answer.type == "VIDEO":
            message = await bot.send_video(chat_id=chat_id, video=answer.file_id_bot, caption=answer.text, reply_to_message_id=answer.to_message_recipient)
        elif answer.type == "VOICE":
            message = await bot.send_voice(chat_id=chat_id, voice=answer.file_id_bot, reply_to_message_id=answer.to_message_recipient)
        elif answer.type == "VIDEO_NOTE":
            message = await bot.send_video_note(chat_id=chat_id, video_note=answer.file_id_bot, reply_to_message_id=answer.to_message_recipient)
        elif answer.type == "ANIMATION":
            message = await bot.send_animation(chat_id=chat_id, animation=answer.file_id_bot, caption=answer.text, reply_to_message_id=answer.to_message_recipient)
        elif answer.type == "AUDIO":
            message = await bot.send_audio(chat_id=chat_id, audio=answer.file_id_bot, reply_to_message_id=answer.to_message_recipient)
        return message
    except Exception as e:
        print(e)
        return "error"


@dp.message_handler(lambda msg: msg.reply_to_message !=None, chat_type=types.ChatType.PRIVATE, content_types=types.ContentTypes.TEXT)
async def user_reply_text(message: types.Message, state: FSMContext):
    if await default_check(types.User.get_current()):
            print(message.chat.id)
            type = "TEXT"
            text = message.parse_entities()
            sender_id = message.from_user.id
            to_message_sender = message.reply_to_message.message_id
            sender_message_id = message.message_id
            answered_to = await postgres.get_answer_by_recipient_message_id(to_message_sender)
            if answered_to == None:
                await message.answer(text="Чтоб ответить на сообщение, сделай реплай по нему,а не по этому сообщению",
                                       reply=message.message_id)
                return
            recipient_id = answered_to.sender_id
            to_message_recipient = answered_to.sender_message_id
            answer = models.Answer()
            answer.text = text
            answer.type = type
            answer.sender_id = sender_id
            answer.to_message_sender = to_message_sender
            answer.sender_message_id = sender_message_id
            answer.recipient_id = recipient_id
            answer.to_message_recipient = to_message_recipient
            answer.status = "SENDING"
            await answer.create()
            await dashboard()
            await bot.send_message(chat_id=data.userbot_id, text=f"/#a:{answer.id}")


@dp.message_handler(lambda msg: msg.reply_to_message !=None, chat_type=types.ChatType.PRIVATE, content_types=['photo', 'video', 'sticker', 'audio', 'animation', 'video_note', 'voice'])
async def user_reply_text(message: types.Message, state: FSMContext):
    if await default_check(types.User.get_current()):
            type = message.content_type.upper()
            answer = models.Answer()
            if type == "PHOTO" or type == "VIDEO" or type == "ANIMATION":
                if message.caption:
                    answer.text = message.html_text
            sender_id = message.from_user.id
            to_message_sender = message.reply_to_message.message_id
            sender_message_id = message.message_id
            answered_to = await postgres.get_answer_by_recipient_message_id(to_message_sender)
            if answered_to == None:
                await message.answer(text="Чтоб ответить на сообщение, сделай реплай по нему,а не по этому сообщению",
                                       reply=message.message_id)
                return
            recipient_id = answered_to.sender_id
            to_message_recipient = answered_to.sender_message_id

            answer.type = type
            print(type)
            if answer.type == "STICKER":
                answer.file_id_bot = message.sticker.file_id
            elif answer.type == "PHOTO":
                answer.file_id_bot = message.photo[-1].file_id
            elif answer.type == "VIDEO":
                answer.file_id_bot = message.video.file_id
            elif answer.type == "VOICE":
                answer.file_id_bot = message.voice.file_id
            elif answer.type == "VIDEO_NOTE":
                answer.file_id_bot = message.video_note.file_id
            elif answer.type == "ANIMATION":
                answer.file_id_bot = message.animation.file_id
            elif answer.type == "AUDIO":
                answer.file_id_bot = message.audio.file_id


            answer.sender_id = sender_id
            answer.to_message_sender = to_message_sender
            answer.sender_message_id = sender_message_id
            answer.recipient_id = recipient_id
            answer.to_message_recipient = to_message_recipient
            answer.status = "SENDING"
            await answer.create()
            await dashboard()
            file = await send_answer(answer, chat_id=data.userbot_id, reply=False)

            await bot.send_message(chat_id=data.userbot_id, text=f"/#a:{answer.id}", reply_to_message_id=file.message_id)