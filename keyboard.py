from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import types
from aiogram.utils.callback_data import CallbackData

menu_cd = CallbackData("show_menu", "level", "id") #"1:2"  #"good:2"
def make_callback_data(level, id=0):
    return menu_cd.new(level=level, id=id)


async def is_correct_keyboard(letter_id):
    letter = await get_letter(letter_id)

    keyboard = InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton(text='Всё верно', callback_data=make_callback_data(level=1)),
        types.InlineKeyboardButton(text='Нет, ошибся', callback_data='bad')
    ]
    keyboard.add(*buttons)
    return keyboard

