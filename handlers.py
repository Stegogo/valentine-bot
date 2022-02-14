import os
import sys
from urllib import request

import aiogram
import requests as requests
from aiogram.dispatcher import FSMContext
from aiogram.types import BotCommandScopeDefault, BotCommandScopeChat, BotCommand, ReplyKeyboardRemove
from aiogram import md
from aiogram.utils.exceptions import MessageNotModified, RetryAfter
from aiogram.utils.markdown import hide_link
from aiograph import Telegraph
import data
import keyboards
import states
import translates

from main import bot, dp
from keyboards import menu_cd, is_correct_keyboard, check_markup, reject_keyboard
from aiogram import types, Dispatcher
import postgres
import models



'''
@dp.message_handler()
async def test(mess: types.Message):
    text = mess.text
    chat = await bot.get_chat(text)
    print(chat)'''

@dp.message_handler(commands=["test_letter"])
async def test_letter(message: types.Message):
    if await default_check(types.User.get_current(), admin=True):
        letter = models.Letter()
        letter.status = "INQUEUE"
        letter.text = "TEST"
        letter.recipient_id = message.from_user.id
        letter.sender_id = message.from_user.id
        letter.sender_message_id = message.message_id
        letter.type = "TEXT"
        if message.from_user.username:
            letter.recipient_username = message.from_user.username
        await letter.create()

@dp.message_handler(commands=["cancel"], state=states.Letter.add_photo_to_text)
async def cancel(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    letter: models.Letter = state_data.get('letter')

    await message.answer(await get_message_to_answer(letter), parse_mode="HTML")

    letter_preview = await message.answer(letter.text, parse_mode="HTML")
    keyboard = await is_correct_keyboard(letter, letter_preview_id=letter_preview.message_id)
    await message.answer(translates.is_correct_question, reply_markup=keyboard, parse_mode="HTML")
    await state.reset_state()


@dp.message_handler(commands=["cancel"], state="*")
async def cancel(message: types.Message, state: FSMContext):
    await message.answer(translates.cancel, reply_markup=ReplyKeyboardRemove())

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



@dp.message_handler(commands=['start'], state="*")
async def send_welcome(message: types.Message):
    if not await default_check(types.User.get_current()):
        await message.answer_sticker(sticker="CAACAgQAAxkBAAIGXV__bWFhszPnWYSQJvKthQoMiem8AAJrAAPOOQgNWWbqY3aSS9AeBA")
        # Срабатывает, если пользователя нет в дб и добавляет его туда
        await message.answer(translates.hello_message)
        await postgres.create_user(message.from_user.id)  #


    start_args = message.get_args()
    if start_args:
        inviter = await postgres.get_user_by_tg_id(int(start_args))
        if inviter:
            letter = models.Letter()
            letter.recipient_id = inviter.tg_id
            letter.recipient_fullname = inviter.fullname
            letter.recipient_username = inviter.username
            letter.by_link = True
            await message.answer(translates.send_me_valentine_from_link.format(recipient_fullname=letter.recipient_fullname))
            await states.Letter.q_text_val.set()
            state = Dispatcher.get_current().current_state()
            await state.update_data(letter=letter)
        else:
            await message.answer(translates.incorrect_link)
    else:
        await message.answer(
            translates.ask_for_username)
        await states.Letter.q_username.set()


@dp.message_handler(commands=['new'], state="*")
async def new_letter(message: types.Message):
    if await default_check(types.User.get_current()):
        await message.answer(translates.ask_for_username)
        await states.Letter.q_username.set()


@dp.message_handler(commands=["my_link"], state='*')
async def my_link(mess: types.Message):
    if await default_check(types.User.get_current()):
        bot_username = (await bot.get_me()).username
        user = types.User.get_current()
        tg_id = user.id
        link = f"https://t.me/{bot_username}?start={tg_id}"
        settings = await postgres.get_settings()
        text=f'{hide_link(settings.instagram_bio_preview)}' + translates.your_link.format(link=link)
        await mess.answer(text, parse_mode='HTML')


'''@dp.message_handler(commands=["language"], state='*', chat_type=types.ChatType.PRIVATE)
async def language(mess: types.Message):
    if await default_check(types.User.get_current()):
        user_in_db = await postgres.get_user_by_tg_id(types.User.get_current().id)
        if not await postgres.get_user_language(user_in_db.tg_id) == "ru":
            keyboard = await keyboards.language_keyboard(user_id=user_in_db.id, current_locale=0)
        else:
            keyboard = await keyboards.language_keyboard(user_id=user_in_db.id, current_locale=1)
        await mess.answer(text=translates.current_language, reply_markup=keyboard)

async def change_language(call: types.CallbackQuery, id, extra_data,  **kwargs):
    if await default_check(types.User.get_current()):
        await call.answer()
        user_in_db = await postgres.get_user(int(id))
        if int(extra_data) == 0:
            locale = "uk"
        else:
            locale = "ru"

        if not  user_in_db.language == locale:
            await user_in_db.update(language=locale).apply()

            if locale == "uk":
                keyboard = await keyboards.language_keyboard(user_id=user_in_db.id, current_locale=0)
            else:
                keyboard = await keyboards.language_keyboard(user_id=user_in_db.id, current_locale=1)
            await call.message.edit_text(text=translates.current_language, reply_markup=keyboard)

async def close_language(call: types.CallbackQuery, **kwargs):
    if await default_check(types.User.get_current()):
        try:
           await call.message.delete()
        except:
            await call.message.delete_reply_markup()'''


@dp.message_handler(state=states.Letter.startpoint)
async def startpoint_handler(message: types.Message):
    await message.answer(translates.ask_for_username)
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

        elif username.startswith('@') and len(username) > 5 and len(username) < 34:
            letter.recipient_username = username[1:]
        elif username.startswith('+'):
            letter.recipient_phone_number = username
        elif message.forward_sender_name:
            await message.answer(translates.account_is_closed.format(forward_sender_name=message.forward_sender_name))
            return
        else:
            await message.answer(translates.incorrect_request)
            return
        await message.answer(translates.ask_for_letter_content)
        await states.Letter.q_text_val.set()
        await state.update_data(letter=letter)


@dp.message_handler(state=states.Letter.q_username, content_types=types.ContentTypes.CONTACT)
async def recipient_contact(message: types.Message, state: FSMContext):
    if await default_check(types.User.get_current()):
        contact = message.contact

        letter = models.Letter()

        if contact.phone_number != None:
            letter.recipient_phone_number = contact.phone_number
        if contact.user_id != None:
            letter.recipient_id = contact.user_id
            letter.recipient_fullname = contact.full_name
        if letter.recipient_phone_number == None and letter.recipient_id == None:
            text = translates.incorrect_contact
            await message.answer(text=text)
        else:
            text = translates.ask_for_letter_content

            await message.answer(text=text)
            await states.Letter.q_text_val.set()
            await state.update_data(letter=letter)

async def get_message_to_answer(letter):
    text = translates.your_letter_will_be_sent_to_1
    if letter.recipient_id != None:
        if letter.recipient_fullname:
            text += f'<a href="tg://user?id={str(letter.recipient_id)}">{str(letter.recipient_fullname)}</a>'
        else:
            text = translates.your_letter_will_be_sent_to_2.format(recipient_id=str(letter.recipient_id))
    elif letter.recipient_username != None:
        text += f"@{letter.recipient_username}"
    elif letter.recipient_phone_number != None:
        text += translates.with_number+ f" {letter.recipient_phone_number}"

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

        await message.answer(await get_message_to_answer(letter), parse_mode="HTML")

        letter_preview = await message.answer(text_val, parse_mode="HTML")
        keyboard = await is_correct_keyboard(letter, letter_preview.message_id)
        await message.answer(translates.is_correct_question, reply_markup=keyboard, parse_mode="HTML")
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

        await message.answer(await get_message_to_answer(letter), parse_mode="HTML")

        letter_preview = await message.answer_photo(photo=letter.file_id_bot, caption=letter.text, parse_mode="HTML")
        keyboard = await is_correct_keyboard(letter, letter_preview.message_id)
        await message.answer(translates.is_correct_question, reply_markup=keyboard, parse_mode="HTML")
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

        await message.answer(await get_message_to_answer(letter), parse_mode="HTML")

        letter_preview = await message.answer_video(video=letter.file_id_bot, caption=letter.text, parse_mode="HTML")
        keyboard = await is_correct_keyboard(letter, letter_preview.message_id)
        await message.answer(translates.is_correct_question, reply_markup=keyboard, parse_mode="HTML")
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

        await message.answer(await get_message_to_answer(letter), parse_mode="HTML")

        letter_preview = await message.answer_animation(animation=letter.file_id_bot, caption=letter.text, parse_mode="HTML")
        keyboard = await is_correct_keyboard(letter, letter_preview.message_id)
        await message.answer(translates.is_correct_question, reply_markup=keyboard, parse_mode="HTML")
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

        await message.answer(await get_message_to_answer(letter), parse_mode="HTML")

        letter_preview = await message.answer_sticker(sticker=letter.file_id_bot)
        keyboard = await is_correct_keyboard(letter, letter_preview.message_id)
        await message.answer(translates.is_correct_question, reply_markup=keyboard, parse_mode="HTML")
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

        await message.answer(await get_message_to_answer(letter), parse_mode="HTML")

        letter_preview = await message.answer_voice(voice=letter.file_id_bot)
        keyboard = await is_correct_keyboard(letter, letter_preview.message_id)
        await message.answer(translates.is_correct_question, reply_markup=keyboard, parse_mode="HTML")
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

        await message.answer(await get_message_to_answer(letter), parse_mode="HTML")

        letter_preview = await message.answer_audio(audio=letter.file_id_bot)
        keyboard = await is_correct_keyboard(letter, letter_preview.message_id)
        await message.answer(translates.is_correct_question, reply_markup=keyboard, parse_mode="HTML")
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

        await message.answer(await get_message_to_answer(letter), parse_mode="HTML")

        letter_preview = await message.answer_video_note(video_note=letter.file_id_bot)
        keyboard = await is_correct_keyboard(letter, letter_preview.message_id)
        await message.answer(translates.is_correct_question, reply_markup=keyboard, parse_mode="HTML")
        await state.reset_state()


@dp.message_handler(state=states.Letter.correct_username)
async def text_val_answer1(message: types.Message, state: FSMContext):
    if await default_check(types.User.get_current()):
        username = message.text
        data = await state.get_data()
        letter : models.Letter = data.get('letter')
        recipient_id=None
        recipient_username = None
        recipient_phone_number=None
        if message.forward_from:
            recipient_id = message.forward_from.id
            if message.forward_from.username:
                recipient_username = message.forward_from.username
        elif username.startswith('@') and len(username) > 5 and len(username) < 34:
            recipient_username = username[1:]
        elif username.startswith('+'):
            recipient_phone_number = username
        elif message.forward_sender_name:
            await message.answer(translates.account_is_closed.format(forward_sender_name=message.forward_sender_name))
            return
        else:
            await message.answer(translates.incorrect_request)
            return
        letter.recipient_id=recipient_id
        letter.recipient_username = recipient_username
        letter.recipient_phone_number = recipient_phone_number
        letter.by_link = False
        await letter.update(recipient_id=recipient_id, recipient_username = recipient_username, recipient_phone_number = recipient_phone_number, by_link = False).apply()
        await message.answer(await get_message_to_answer(letter), parse_mode="HTML")

        letter_preview = await send_letter(letter, chat_id=message.chat.id)
        keyboard = await is_correct_keyboard(letter, letter_preview.message_id)
        await message.answer(translates.is_correct_question, reply_markup=keyboard, parse_mode="HTML")
        await state.reset_state()

@dp.message_handler(state=states.Letter.correct_username, content_types=types.ContentTypes.CONTACT)
async def change_recipient_receive_contact(message: types.Message, state: FSMContext):
    if await default_check(types.User.get_current()):
        contact = message.contact

        data = await state.get_data()
        letter = data.get("letter")
        letter.recipient_id = None
        letter.recipient_username = None
        letter.recipient_phone_number = None

        if contact.phone_number != None:
            letter.recipient_phone_number = contact.phone_number
        if contact.user_id != None:
            letter.recipient_id = contact.user_id
            letter.recipient_fullname = contact.full_name
        if letter.recipient_phone_number == None and letter.recipient_id == None:
            text = translates.incorrect_contact
            await message.answer(text=text)
        else:
            await letter.update(recipient_id=letter.recipient_id, recipient_username=letter.recipient_username,
                                recipient_phone_number=letter.recipient_phone_number, recipient_fullname=letter.recipient_fullname).apply()
            await message.answer(await get_message_to_answer(letter), parse_mode="HTML")

            letter_preview = await send_letter(letter, chat_id=message.chat.id)
            keyboard = await is_correct_keyboard(letter, letter_preview.message_id)
            await message.answer(translates.is_correct_question, reply_markup=keyboard, parse_mode="HTML")
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
        await message.answer(translates.is_correct_question, reply_markup=keyboard, parse_mode="HTML")
        await state.reset_state()

@dp.message_handler(state=states.Letter.add_photo_to_text, content_types=types.ContentTypes.ANY)
async def add_photo_to_text_not_photo(message: types.Message, state: FSMContext):
    if await default_check(types.User.get_current()):
        await message.answer(translates.ask_for_photo)



async def process_callback_button1(callback_query: types.CallbackQuery, id,**kwargs):
    if await default_check(types.User.get_current()):
        await bot.answer_callback_query(callback_query.id)
        await callback_query.message.edit_text(translates.ask_for_correct_username)
        await states.Letter.correct_username.set()
        state = Dispatcher.get_current().current_state()
        letter = await postgres.get_letter(int(id))
        await state.update_data(letter=letter)

async def process_callback_button2(callback_query: types.CallbackQuery, id, **kwargs):
    if await default_check(types.User.get_current()):
        await bot.answer_callback_query(callback_query.id)
        await callback_query.message.edit_text(translates.ask_for_correct_letter_content)
        await states.Letter.q_text_val.set()
        state = Dispatcher.get_current().current_state()
        letter = await postgres.get_letter(int(id))
        await state.update_data(letter=letter)

async def add_photo_to_text(callback_query: types.CallbackQuery, id, extra_data, **kwargs):
    if await default_check(types.User.get_current()):
        await bot.answer_callback_query(callback_query.id)
        await callback_query.message.edit_text(translates.ask_for_photo)
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


        try:
            await callback_query.message.delete()
        except:
            await callback_query.message.edit_text("Отправляю...")
            await callback_query.message.delete_reply_markup()
        await callback_query.message.answer(translates.your_letter_sended_to_admins)

        if not letter.recipient_username and letter.recipient_id:
            await bot.send_message(chat_id=data.userbot_id, text=f"/#u:{letter.id}")
        else:
            letter.status = "INQUEUE"
            await letter.update(status = "INQUEUE").apply()



async def scan_queue():
    checking_letters = await postgres.count_checking_letters()
    settings = await postgres.get_settings()
    if settings.is_send_to_moders:
        letter = await postgres.get_letter_in_queue()
        if letter:
            if checking_letters < 3:
                letter.status = "CHECKING"
                moder_chat_id = (await postgres.get_settings()).moder_chat_id
                admin_mess_1 = await bot.send_message(chat_id=moder_chat_id, text=await get_admin_message_text(letter),
                                                      parse_mode="HTML")
                await send_letter(letter, chat_id=moder_chat_id)
                letter.admin_message_id = admin_mess_1.message_id
                await letter.update(admin_message_id=admin_mess_1.message_id, status="CHECKING").apply()

                markup = await keyboards.check_markup(letter=letter)
                text = "Что сделать?"
                if letter.recipient_username == None and letter.recipient_id != None:
                    userbot = await postgres.get_user_by_tg_id(data.userbot_id)
                    text += f"\nЧтоб отправить сообщение этому юзеру, {userbot.fullname} должен вручную начать диалог. Когда чат будет создан, {userbot.fullname} должен нажать кнопку ниже"
                await bot.send_message(chat_id=moder_chat_id, text=text, reply_markup=markup)
            else:
                moder_chat_id = (await postgres.get_settings()).moder_chat_id
                await bot.send_message(chat_id=moder_chat_id, text="Обработайте валентинки, в очереди есть еще")






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
        try:
            letter = await postgres.get_letter(int(id))
            keyboard = await keyboards.add_contact_keyboard(letter)
            await call.message.edit_text("Пришли айди или юзернейм получателя с реплаем на это сообщение", reply_markup=keyboard)
            await states.Letter.add_receiver_contact.set()
            state = Dispatcher.get_current().current_state()
            await bot.answer_callback_query(call.id)
            await state.update_data(letter_id=id)
        except RetryAfter as e:
            print(e)
            await call.answer(text="Флуд Бан, нажми через несколько секунд")


@dp.message_handler(state=states.Letter.add_receiver_contact)
async def add_receiver_contact(message: types.Message, state: FSMContext):
    if await default_check(types.User.get_current(), admin=True):
        try:
            state_data = await state.get_data()
            letter: models.Letter = await postgres.get_letter(int(state_data.get("letter_id")))
            if message.text.startswith("@") and len(message.text) > 5 and len(message.text) < 34:
                letter.recipient_username = message.text[1:]
                await letter.update(recipient_username = message.text[1:]).apply()
            elif message.text.isdigit():
                letter.recipient_id = int(message.text)
                await letter.update(recipient_id = int(message.text)).apply()

            else:
                await message.answer("Ошибка. Пришли мне юзернейм или айди получателя", reply=message.message_id)
                return

            moder_chat_id = (await postgres.get_settings()).moder_chat_id
            await bot.edit_message_text(chat_id=moder_chat_id, message_id=int(letter.admin_message_id), text=await get_admin_message_text(letter), parse_mode="HTML")
            if message.reply_to_message != None:
                keyboard = await keyboards.check_markup(letter)
                await message.reply_to_message.edit_text("Что сделать?", reply_markup=keyboard)
            await message.answer(text="Принято", reply=message.message_id)

            await state.reset_state()
        except RetryAfter as e:
            print(e)



@dp.message_handler(state=states.Letter.reject_reason)
async def reject_text(message: types.Message, state: FSMContext):
    if await default_check(types.User.get_current(), admin=True):
        try:
            state_data = await state.get_data()
            letter: models.Letter = await postgres.get_letter(int(state_data.get("letter_id")))
            letter.reject_reason = message.text
            letter.status = "REJECTED"
            await letter.update(reject_reason=message.text, status="REJECTED").apply()

            await bot.send_message(chat_id=letter.sender_id, text=translates.reject.format(reject_reason=letter.reject_reason),
                                   reply_to_message_id=letter.sender_message_id)
            moder_chat_id = (await postgres.get_settings()).moder_chat_id
            await bot.edit_message_text(chat_id=moder_chat_id, message_id=int(letter.admin_message_id), text=await get_admin_message_text(letter), parse_mode="HTML")
            if message.reply_to_message != None:
                await message.reply_to_message.edit_text("Валентинка відхилена")
            await message.answer(text="Отправлено", reply=message.message_id)

            await state.reset_state()
        except RetryAfter as e:
            print(e)



async def initialisate_chat_with_user(call: types.CallbackQuery, id, **kwargs):
    if await default_check(types.User.get_current(), admin=True):
        try:
            await bot.answer_callback_query(call.id)
            if types.User.get_current().id == data.userbot_id:

                letter= await postgres.get_letter(int(id))
                markup = await keyboards.delivery_confirm_markup(letter=letter)
                await call.message.edit_text(text="Ты точно начал диалог?\nЕсли нет, то сообщение не сможет отправиться",
                                             reply_markup=markup)
            else:
                await bot.answer_callback_query(callback_query_id=call.id, text="Эту кнопку должен нажать акк юзербота",
                                                show_alert=True)
        except RetryAfter as e:
            print(e)
            await call.answer(text="Флуд Бан, нажми через несколько секунд")


async def reject_letter(call: types.CallbackQuery, id, **kwargs):
    if await default_check(types.User.get_current(), admin=True):
        try:
            await bot.answer_callback_query(call.id)
            letter = await postgres.get_letter(int(id))
            keyboard = await reject_keyboard(letter=letter)
            await call.message.edit_text("Напиши причину отказа реплаем на это сообщение", reply_markup=keyboard)

            await states.Letter.reject_reason.set()
            state = Dispatcher.get_current().current_state()
            await state.update_data(letter_id=id)
        except RetryAfter as e:
            print(e)
            await call.answer(text="Флуд Бан, нажми через несколько секунд")

async def approve_letter(call: types.CallbackQuery, id, extra_data, **kwargs):
    if await default_check(types.User.get_current(), admin=True):
        await bot.answer_callback_query(call.id)
        if int(extra_data) == 1 and types.User.get_current().id == data.userbot_id or int(extra_data) == 0:
            try:
                await call.message.edit_text("Валентинка принята")
                letter: models.Letter = await postgres.get_letter(int(id))

                letter.status = "APPROVED"
                await letter.update(status="APPROVED").apply()

                if letter.type == "TEXT":
                    await bot.send_message(chat_id=data.userbot_id, text=f"/#l:{letter.id}")
                else:
                    file = await send_letter(letter=letter, chat_id=data.userbot_id)
                    await bot.send_message(chat_id=data.userbot_id, text=f"/#l:{letter.id}",
                                           reply_to_message_id=file.message_id)
                moder_chat_id = (await postgres.get_settings()).moder_chat_id
                await bot.edit_message_text(chat_id=moder_chat_id, message_id=int(letter.admin_message_id),
                                            text=await get_admin_message_text(letter), parse_mode="HTML")
            except RetryAfter as e:
                print(e)
                await bot.answer_callback_query(call.id, text="Флуд Бан, нажми через несколько секунд")
        else:
            await bot.answer_callback_query(callback_query_id=call.id, text="Эту кнопку должен нажать акк юзербота",
                                            show_alert=True)

#@dp.message_handler(lambda message: message.chat_id == data.moder_chat_id, commands=["add_admin"], chat_type=types.ChatType.GROUP)
@dp.message_handler(lambda message: message.chat.id == data.moder_chat_id, commands=["add_admin"])
async def add_admin(mess: types.Message):
    if await default_check(types.User.get_current(), admin=True):
        message_array = mess.text.split(" ")
        admin_contact = message_array[-1]
        try:
            if admin_contact.startswith("@") and len(admin_contact) > 5 and len(admin_contact) < 34:
                user_in_db = await postgres.get_user_by_username(admin_contact[1:])
                if user_in_db:
                    if user_in_db.is_admin:
                        await mess.answer(f"{admin_contact} и так админ", reply=mess.message_id)
                    else:
                        await user_in_db.update(is_admin=True).apply()
                        await mess.answer(f"{admin_contact} назначен админом", reply=mess.message_id)
                        await set_personal_bot_commands(user_in_db.id)

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

                else:
                    await mess.answer("Не нашел такого человека в базе", reply=mess.message_id)
            else:
                await mess.answer("Формат команды <code>/add_admin id_or_username</code>", reply=mess.message_id, parse_mode="HTML")
        except RetryAfter as e:
            print(e)


@dp.message_handler(lambda message: message.chat.id == data.moder_chat_id, commands=["del_admin"])
async def del_admin(mess: types.Message):
    if await default_check(types.User.get_current(), admin=True):
        try:
            message_array = mess.text.split(" ")
            admin_contact = message_array[-1]
            if admin_contact.startswith("@") and len(admin_contact) > 5 and len(admin_contact) < 34:
                user_in_db = await postgres.get_user_by_username(admin_contact[1:])
                if user_in_db:
                    if not user_in_db.is_admin:
                        await mess.answer(f"{admin_contact} и так не админ", reply=mess.message_id)
                    else:
                        await user_in_db.update(is_admin=False).apply()
                        await mess.answer(f"{admin_contact} больше не админ", reply=mess.message_id)
                        await set_personal_bot_commands(user_in_db.id)

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

                else:
                    await mess.answer("Не нашел такого человека в базе", reply=mess.message_id)
            else:
                await mess.answer("Формат команды <code>/del_admin id_or_username</code>", reply=mess.message_id, parse_mode="HTML")
        except RetryAfter as e:
            print(e)

@dp.message_handler(lambda message: message.chat.id == data.moder_chat_id, commands=["start_queue"])
async def start_queue(mess: types.Message):
    if await default_check(types.User.get_current(), admin=True):
        try:
            settings = await postgres.get_settings()
            if settings:
                if settings.is_send_to_moders:
                    await mess.answer(f"Валентинки и так присылаются", reply=mess.message_id)
                else:
                    await settings.update(is_send_to_moders=True).apply()
                    await mess.answer(f"Теперь валентинки из очереди будут присылаться в чат админов", reply=mess.message_id)

        except RetryAfter as e:
            print(e)


@dp.message_handler(lambda message: message.chat.id == data.moder_chat_id, commands=["stop_queue"])
async def stop_queue(mess: types.Message):
    if await default_check(types.User.get_current(), admin=True):
        try:
            settings = await postgres.get_settings()
            if settings:
                if not settings.is_send_to_moders:
                    await mess.answer(f"Валентинки и так не присылаются", reply=mess.message_id)
                else:
                    await settings.update(is_send_to_moders=False).apply()
                    await mess.answer(f"Теперь валентинки из очереди не будут присылаться в чат админов",
                                      reply=mess.message_id)

        except RetryAfter as e:
            print(e)


@dp.message_handler(lambda message: message.chat.id == data.moder_chat_id, commands=["change_moder_chat_id"])
async def change_moder_chat_id(mess: types.Message):
    if await default_check(types.User.get_current(), admin=True):
        try:
            settings = await postgres.get_settings()
            message_array = mess.text.split(" ")
            moder_chat_id = message_array[-1]
            if moder_chat_id.isdigit():
                if int(moder_chat_id) == settings.moder_chat_id:
                    await mess.answer(f'Это и так чат модераторов', parse_mode="HTML",
                                      reply=mess.message_id)
                else:
                    settings.moder_chat_id = int(moder_chat_id)
                    await settings.update(moder_chat_id = int(moder_chat_id)).apply()
                    await mess.answer(f'Чат модераторов изменен, новые валентинки будут приходить туда', parse_mode="HTML",
                                      reply=mess.message_id)

            else:
                await mess.answer("Формат команды <code>/change_moder_chat_id chat_id</code>", reply=mess.message_id,
                                  parse_mode="HTML")
        except RetryAfter as e:
            print(e)




async def admin_menu(call: types.CallbackQuery, id, **kwargs):
    if await default_check(types.User.get_current(), admin=True):
        try:
            await bot.answer_callback_query(call.id)
            letter = await postgres.get_letter(int(id))
            keyboard = await check_markup(letter)
            await call.message.edit_text(text="Что сделать?", reply_markup=keyboard)
        except RetryAfter as e:
            print(e)
            await call.answer(text="Флуд Бан, нажми через несколько секунд")


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
        moder_chat_id = (await postgres.get_settings()).moder_chat_id
        if message.text.startswith("/#"):
            message_dict = message.text[2:].split(":")
            if message_dict[0] == "ls":
                # successfull delivery
                letter = await postgres.get_letter(int(message_dict[1]))

                letter.status = "DELIVERED"
                await letter.update(status="DELIVERED").apply()



                await bot.edit_message_text(chat_id=moder_chat_id, message_id=int(letter.admin_message_id),
                                            text=await get_admin_message_text(letter), parse_mode="HTML")
                await bot.send_message(chat_id=letter.sender_id,
                                       text=translates.successfull_letter_delivery,
                                       reply_to_message_id=letter.sender_message_id)
            elif message_dict[0] == "le":
                # error delivery
                letter = await postgres.get_letter(int(message_dict[1]))

                letter.status = "ERROR"
                await letter.update(status="ERROR").apply()



                await bot.edit_message_text(chat_id=moder_chat_id, message_id=int(letter.admin_message_id),
                                            text=await get_admin_message_text(letter), parse_mode="HTML")
                await bot.send_message(chat_id=letter.sender_id,
                                       text=translates.error_letter_delivery,
                                       reply_to_message_id=letter.sender_message_id)
            elif message_dict[0] == "a":
                answer = await postgres.get_answer(int(message_dict[1]))

                try:
                    if answer.type != "TEXT" and message.reply_to_message != None:
                        answer.file_id_bot = await postgres.get_file_id(answer, message.reply_to_message)
                    await bot.send_message(chat_id=answer.recipient_id, text=translates.new_answer)
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
                                       text=translates.error_answer_delivery,
                                       reply_to_message_id=answer.sender_message_id)
            elif message_dict[0] == "as":
                # successfull delivery
                answer = await postgres.get_answer(int(message_dict[1]))
                await bot.send_message(chat_id=answer.sender_id, text=translates.successfull_answer_delivery,
                                       reply_to_message_id=answer.sender_message_id)
            elif message_dict[0] == "ue":
                # error delivery
                letter = await postgres.get_letter(int(message_dict[1]))

                letter.status = "INQUEUE"
                await letter.update(status="INQUEUE").apply()

            elif message_dict[0] == "us":
                # successfull delivery
                letter = await postgres.get_letter(int(message_dict[1]))
                letter.status = "INQUEUE"
                await letter.update(status="INQUEUE").apply()



async def set_personal_bot_commands(user_id):
    user = await postgres.get_user(user_id)
    if user and user.is_admin:
        commands = [BotCommand(command="new", description=translates.new_command),
                    BotCommand(command="my_link", description=translates.my_link_command),
                ]
    else:
        commands = [BotCommand(command="new", description=translates.new_command),
                    BotCommand(command="my_link", description=translates.my_link_command),
                            ]
    await bot.set_my_commands(commands=commands, scope=BotCommandScopeChat(user.tg_id))

async def set_bot_commands():
    commands_default = [BotCommand(command="new", description=translates.new_command),
                        BotCommand(command="my_link", description=translates.my_link_command),
                ]
    commands_admin_chat = [BotCommand(command="add_admin", description=translates.add_admin_command),
                    BotCommand(command="del_admin", description=translates.del_admin_command),
                    BotCommand(command="new", description=translates.new_command),
                           BotCommand(command="my_link", description=translates.my_link_command),
                           BotCommand(command="start_queue", description="Открыть обработку очереди"),
                           BotCommand(command="stop_queue", description="Закрыть обработку очереди"),
                           BotCommand(command="change_moder_chat_id", description="Смена чата модеров"),
                        ]
    moder_chat_id = (await postgres.get_settings()).moder_chat_id
    await bot.set_my_commands(commands=commands_default, scope=BotCommandScopeDefault())
    await bot.set_my_commands(commands=commands_admin_chat, scope=BotCommandScopeChat(moder_chat_id))

async def dashboard():
    moder_chat_id = (await postgres.get_settings()).moder_chat_id
    users_size = await postgres.count_users()
    bot_blocked_users = await postgres.count_bot_blocked_users()
    blocked_by_bot_users = await postgres.count_blocked_by_bot_users()
    admin_users = await postgres.count_admin_users()
    letters_size = await postgres.count_letters()
    answers_size = await postgres.count_answers()
    delivered_letters = await postgres.count_delivered_letters()
    queue_letters = await postgres.count_queue_letters()
    approved_letters = await postgres.count_approved_letters()
    error_letters = await postgres.count_error_letters()
    creating_letters = await postgres.count_creating_letters()
    checking_letters = await postgres.count_checking_letters()
    rejected_letters = await postgres.count_rejected_letters()
    sending_answers = await postgres.count_sending_answers()
    error_answers = await postgres.count_error_answers()
    delivered_answers = await postgres.count_delivered_answers()
    text=f"Людей в базе: {users_size}\nЗаблокировали бота: {bot_blocked_users}\nЗаблокированы ботом: {blocked_by_bot_users}\nАдмины: {admin_users}\n\n" \
         f"Валентинок в базе: {letters_size}\nВ очереди: {queue_letters}\nУспешно доставлено: {delivered_letters}\nНа проверке: {checking_letters}\nВ процессе создания: {creating_letters}\n" \
         f"Ошибка доставки: {error_letters}\nОтклонено: {rejected_letters}\nПроверено, но не доставлено: {approved_letters}\n\n" \
         f"Ответов в базе: {answers_size}\nУспешно доставлено: {delivered_answers}\nОшибка доставки: {error_answers}\nДоставляется: {sending_answers}"
    try:
        settings = await postgres.get_settings()
        await bot.edit_message_text(chat_id=moder_chat_id, message_id=settings.dashboard_message_id, text=text)
    except AttributeError as e:
        print("error dashboard:")
        print(e)
        mess =await bot.send_message(chat_id=moder_chat_id, text=text)
        with open("data.py", 'a') as f:
            f.write(f'\ndashboard_message_id = {mess.message_id}')
            f.close()
            await bot.send_message(chat_id=moder_chat_id, text="Файл data перезаписан, перезапусти бота")
            sys.exit()
    except MessageNotModified as e:
        pass



async def send_letter(letter, chat_id):

    message = None
    if letter.type == "TEXT":
        message = await bot.send_message(chat_id=chat_id, text=letter.text, parse_mode="HTML", disable_web_page_preview=not letter.link_preview)
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

            type = "TEXT"
            text = message.parse_entities()
            sender_id = message.from_user.id
            to_message_sender = message.reply_to_message.message_id
            sender_message_id = message.message_id
            answered_to = await postgres.get_answer_by_recipient_message_id(to_message_sender, sender_id)
            if answered_to == None:
                await message.answer(text=translates.reply_to_answer,
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
            answered_to = await postgres.get_answer_by_recipient_message_id(to_message_sender, sender_id)
            if answered_to == None:
                await message.answer(text=translates.reply_to_answer,
                                       reply=message.message_id)
                return
            recipient_id = answered_to.sender_id
            to_message_recipient = answered_to.sender_message_id

            answer.type = type

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

            file = await send_answer(answer, chat_id=data.userbot_id, reply=False)

            await bot.send_message(chat_id=data.userbot_id, text=f"/#a:{answer.id}", reply_to_message_id=file.message_id)