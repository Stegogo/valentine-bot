from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import types
from aiogram.utils.callback_data import CallbackData
import models


menu_cd = CallbackData("show_menu", "level", "id", "extra_data")

def make_callback_data(level, id=0, extra_data=0):
    return menu_cd.new(level=level, id=id, extra_data=extra_data)

async def reject_keyboard(letter):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.row(InlineKeyboardButton(text='Не отклонять', callback_data=make_callback_data(level=7, id=letter.id)))

    return keyboard

async def add_contact_keyboard(letter):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.row(InlineKeyboardButton(text='Назад', callback_data=make_callback_data(level=7, id=letter.id)))

    return keyboard

async def is_correct_keyboard(letter, letter_preview_id):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.row(types.InlineKeyboardButton(text='Изменить получателя', callback_data=make_callback_data(level=1, id=letter.id)))
    keyboard.row(types.InlineKeyboardButton(text='Изменить валентинку', callback_data=make_callback_data(level=2, id=letter.id)))

    if letter.type == "TEXT":
        if '>&#8288;</a>' in letter.text:
            keyboard.row(InlineKeyboardButton(text="Убрать фото", callback_data=make_callback_data(level=10, id=letter.id, extra_data=letter_preview_id)))
        else:
            keyboard.row(InlineKeyboardButton(text="Добавить фото", callback_data=make_callback_data(level=9, id=letter.id, extra_data=letter_preview_id)))
            if letter.link_preview == True and "a href=" in letter.text:

                keyboard.row(InlineKeyboardButton(text="Выключить предпросмотр", callback_data=make_callback_data(level=11, id=letter.id, extra_data=letter_preview_id)))
            elif letter.link_preview == False and "a href=" in letter.text:

                keyboard.row(InlineKeyboardButton(text="Включить предпросмотр", callback_data=make_callback_data(level=12, id=letter.id, extra_data=letter_preview_id)))
    keyboard.row(types.InlineKeyboardButton(text='Всё верно, отправить на проверку', callback_data=make_callback_data(level=3, id=letter.id)))


    return keyboard

async def check_markup(letter: models.Letter, is_userbot_can_write_to_user_by_id=False):
    markup = InlineKeyboardMarkup()
    if letter.recipient_id == None and letter.recipient_username == None and letter.recipient_phone_number:
            markup.row(InlineKeyboardButton(text="Добавить данные получателя", callback_data=make_callback_data(level=4, id=letter.id)))
    

    else:
        if letter.recipient_username or is_userbot_can_write_to_user_by_id:
            markup.row(InlineKeyboardButton(text="Принять", callback_data=make_callback_data(level=8, id=letter.id)))
        else:
            markup.row(InlineKeyboardButton(text="Я написал первое сообщение", callback_data=make_callback_data(level=5, id=letter.id)))
    markup.row(InlineKeyboardButton(text="Отклонить", callback_data=make_callback_data(level=6, id=letter.id)))
    return markup

async def delivery_confirm_markup(letter: models.Letter):
    markup = InlineKeyboardMarkup()


    markup.row(InlineKeyboardButton(text="Отправить валентинку", callback_data=make_callback_data(level=8, id=letter.id, extra_data=1)))


    markup.row(InlineKeyboardButton(text="Назад", callback_data=make_callback_data(level=7, id=letter.id)))
    return markup