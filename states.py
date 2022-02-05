from aiogram.dispatcher.filters.state import State, StatesGroup


class Letter(StatesGroup):
    startpoint = State()
    q_username = State()
    q_text_val = State()

    correct_username = State()
    correct_val = State()
    endpoint = State()

