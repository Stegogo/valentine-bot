from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton




from aiogram import types

keyboard = InlineKeyboardMarkup(row_width=2)
buttons = [
    types.InlineKeyboardButton(text='Всё верно', callback_data='good'),
    types.InlineKeyboardButton(text='Нет, ошибся', callback_data='bad')
]
keyboard.add(*buttons)


