from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import types
from aiogram.utils.callback_data import CallbackData
import models


menu_cd = CallbackData("show_menu", "level", "id")

def make_callback_data(level, id=0):
    return menu_cd.new(level=level, id=id)

keyboard = InlineKeyboardMarkup(row_width=1)
buttons = [
    types.InlineKeyboardButton(text='Изменить юзернейм', callback_data=make_callback_data(level=1, id=models.User.id)),
    types.InlineKeyboardButton(text='Изменить валентинку', callback_data=make_callback_data(level=2, id=models.User.id)),
    types.InlineKeyboardButton(text='Всё верно, отправить на проверку', callback_data=make_callback_data(level=3, id=models.User.id))
]
keyboard.add(*buttons)


