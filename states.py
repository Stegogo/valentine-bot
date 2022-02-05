from aiogram.dispatcher.filters.state import State, StatesGroup


class Letter(StatesGroup):
    q_username = State()
    q_text_val = State()
    send_to_moder = State()
    correct_username = State()

