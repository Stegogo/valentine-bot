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

