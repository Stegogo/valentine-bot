from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import types
from aiogram.utils.callback_data import CallbackData

menu_cd = CallbackData("show_menu", "level", "id") #"1:2"  #"good:2"
def make_callback_data(level, id=0):
    return menu_cd.new(level=level, id=id)


async def is_correct_keyboard(letter_id):
    letter = await get_letter(letter_id)

<<<<<<< Updated upstream
    keyboard = InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton(text='Всё верно', callback_data=make_callback_data(level=1)),
        types.InlineKeyboardButton(text='Нет, ошибся', callback_data='bad')
    ]
    keyboard.add(*buttons)
    return keyboard
=======
from aiogram import types
menu_cd = CallbackData("show_menu", "level", "id", "data_1") #"good:1:3:3"


def make_callback_data(level, id=0, data_1=0):
    return menu_cd.new(level=level, id=id, i=i, id2=id2)

keyboard = InlineKeyboardMarkup(row_width=2)
buttons = [
    types.InlineKeyboardButton(text='Всё верно', callback_data=make_callback_data(level=1, id=user.id)),
    types.InlineKeyboardButton(text='Нет, ошибся', callback_data='bad')
]
keyboard.add(*buttons)

>>>>>>> Stashed changes

