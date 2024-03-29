from aiogram.dispatcher.filters.state import State, StatesGroup


class Letter(StatesGroup):
    q_username = State()
    q_text_val = State()
    correct_username = State()
    correct_val = State()
    startpoint = State()
    endpoint = State()
    add_receiver_contact = State()
    add_photo_to_text = State()
    reject_reason = State()
