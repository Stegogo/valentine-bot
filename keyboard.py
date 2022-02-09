from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import types
from aiogram.utils.callback_data import CallbackData
import models


menu_cd = CallbackData("show_menu", "level", "id")

def make_callback_data(level, id=0):
    return menu_cd.new(level=level, id=id)

async def reject_keyboard(letter):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.row(InlineKeyboardButton(text='Не отклонять', callback_data=make_callback_data(level=7, id=letter.id)))

    return keyboard

async def is_correct_keyboard(letter):
    keyboard = InlineKeyboardMarkup(row_width=1)
    buttons = [
        types.InlineKeyboardButton(text='Изменить юзернейм', callback_data=make_callback_data(level=1, id=letter.id)),
        types.InlineKeyboardButton(text='Изменить валентинку', callback_data=make_callback_data(level=2, id=letter.id)),
        types.InlineKeyboardButton(text='Всё верно, отправить на проверку', callback_data=make_callback_data(level=3, id=letter.id))
    ]
    keyboard.add(*buttons)
    return keyboard

async def check_markup(letter: models.Letter):
    markup = InlineKeyboardMarkup()
    if letter.recipient_id == None and letter.recipient_username == None and letter.recipient_phone_number:
            markup.row(InlineKeyboardButton(text="Добавить данные получателя", callback_data=make_callback_data(level=4, id=letter.id)))
    if letter.recipient_username:
        markup.row(InlineKeyboardButton(text="Я написал первое сообщение", callback_data=make_callback_data(level=5, id=letter.id)))

    else:
        if letter.recipient_username:
            markup.row(InlineKeyboardButton(text="Принять", callback_data=make_callback_data(level=2, id=letter.id)))
        else:
            markup.row(InlineKeyboardButton(text="Я написал первое сообщение", callback_data=make_callback_data(level=5, id=letter.id)))
    markup.row(InlineKeyboardButton(text="Отклонить", callback_data=make_callback_data(level=6, id=letter.id)))
    return markup

