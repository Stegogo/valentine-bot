from aiogram.dispatcher import FSMContext
<<<<<<< Updated upstream
from states import Letter
=======
import Letter_class

>>>>>>> Stashed changes
from main import bot, dp
from keyboard import is_correct_keyboard, menu_cd
from aiogram import types
import postgres
from models import Letter
from aiogram.dispatcher.filters import Command
from keyboard import is_correct_keyboard

@dp.my_chat_member_handler()
async def chat_update(my_chat_member: types.ChatMemberUpdated):
    user = types.User.get_current()
    user_in_DB: User = await get_user(user.id)
    if user_in_DB:
        if my_chat_member.new_chat_member.status == "kicked":
            text = f'<a href="tg://user?id={str(user_in_DB.tg_id)}">{str(user_in_DB.fullname)}</a> заблокировал бота'
            await bot.send_message(chat_id=243568187, text=text, parse_mode="HTML")
            await user_in_DB.update(is_bot_blocked=True).apply()
        elif my_chat_member.new_chat_member.status == "member":

            text = f'<a href="tg://user?id={str(user_in_DB.tg_id)}">{str(user_in_DB.fullname)}</a> разблокировал бота'
            await bot.send_message(chat_id=243568187, text=text, parse_mode="HTML")
            await user_in_DB.update(is_bot_blocked=False).apply()




@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):

    user = types.User.get_current()
    tg_id = user.id
    isUserAlreadyInDB = await get_user(tg_id)
    users = await postgres.main()

    if not isUserAlreadyInDB:

        user_in_db = postgres.User()
        user_in_db.username = user.username
        user_in_db.fullname = user.fullname
        await user_in_db.create()
        await message.answer("Привет! Я бот, который отправляет поздравления другим людям!")
        print("Вас нет в базе данных")
        await postgres.create(message.from_user.id)
        await message.answer('Отправь нам @юзернейм твоей радости🥰')
<<<<<<< Updated upstream
        await Letter.q_username.set()
=======
        await states.Letter.q_username.set()
        

@dp.message_handler(state=states.Letter.q_username)
async def username_answer(message: types.Message, state: FSMContext):
    username = message.text
    if username.startswith('@'):
        await state.update_data(answer1=username)
        await message.answer('Супер! Мы нашли его! Теперь мы ждём текст твоей валентинки🧐')
        await states.Letter.q_text_val.set()
>>>>>>> Stashed changes
    else:
        # Кидаем здесь нужный стейт
        print("Вы есть в базе данных")
        state = Dispatcher.get_current().current_state()
        if state == Letter.q_username:
            await message.answer('Отправь нам @юзернейм твоей радости🥰')
        if state == None:
            await message.answer("Привет! Я бот, который отправляет поздравления другим людям!")



@dp.message_handler(state=Letter.q_username)
async def username_answer(message: types.Message, state: FSMContext):
    user = types.User.get_current()
    user_in_DB: User = await get_user(user.id)
    if user_in_DB:
        if not user_in_DB.is_bot_blocked:
            username = message.text
            if username.startwith("@"):
                await state.update_data(answer1=username)
                await message.answer('Супер! Мы нашли его! Теперь мы ждём текст твоей валентинки🧐')
                await Letter.q_text_val.set()
            else:
                pass

@dp.message_handler(state=Letter.q_text_val)
async def text_val_answer(message: types.Message, state: FSMContext):
    data = await state.get_data()
    username = data.get('answer1')
    text_val = message.text
<<<<<<< Updated upstream
    await message.answer('Я всё правильно понял?')
    await message.answer(f'Твоя валентинка будет отправлена пользователю {username}')
    await message.answer('Текст валентинки: ')
    keyboard = await is_correct_keyboard(123)
=======
    letter = Letter()
    letter.recipient_username = username
    letter.text = text_val

    letter = await letter.create()

    await state.update_data(answer2=text_val)
    await message.answer('Я всё правильно понял?')
    await message.answer(f'Твоя валентинка будет отправлена пользователю {username}')
    await message.answer('Текст валентинки: ')
    keyboard = await keyboards.is_correct_markup(letter)
>>>>>>> Stashed changes
    await message.answer(text_val, reply_markup=keyboard)
    await state.finish()


<<<<<<< Updated upstream
async def process_callback_button1(callback_query: types.CallbackQuery, **kwargs):
=======
async def process_callback_button1(callback_query: types.CallbackQuery, id, data_1):
>>>>>>> Stashed changes
    await bot.answer_callback_query(callback_query.id)
    letter = await get_letter(id)
    await bot.send_message(callback_query.from_user.id, 'Мы всё записали) Хорошего дня!')
    letter = Letter()
    letter.sender_message_id = 
    

<<<<<<< Updated upstream
=======
async def process_callback_button2(callback_query: types.CallbackQuery, **kwargs):
    
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Отправь новую валентинку')
    await states.Letter.correct_val.set()
>>>>>>> Stashed changes

<<<<<<< Updated upstream

<<<<<<< Updated upstream
async def process_callback_button2(callback_query: types.CallbackQuery, **kwargs):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Отправь нам @юзернейм твоей радости🥰')
    await Letter.q_username.set()
=======

async def process_callback_button3(callback_query: types.CallbackQuery, id, **kwargs):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Отправили!')
    letter = await get_letter(int(id))
    await bot.send_message(-772205304, 'Юзернейм')
    await bot.send_message(-772205304, letter.recipient_username)
    await bot.send_message(-772205304, 'Текст валентинки')
    await bot.send_message(-772205304, letter.text)
>>>>>>> Stashed changes

=======
@dp.callback_query_handler(lambda c: c.data == 'bad')
async def process_callback_button2(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Отправь нам @юзернейм твоей радости🥰')
    await Letter_class.Letter.q_username.set()
>>>>>>> Stashed changes


@dp.callback_query_handler(menu_cd.filter(), state="*")
async def navigate(call: types.CallbackQuery, callback_data: dict):
    current_level = callback_data.get('level')
    id = callback_data.get('id')
<<<<<<< Updated upstream


    levels = {
        "1": process_callback_button1,
        "2": process_callback_button2,

=======
    data_1 = callback_data.get('data_1')
    

    levels = {
        "1": process_callback_button1,
        
>>>>>>> Stashed changes

    }

    current_level_function = levels[current_level]

    await current_level_function(
<<<<<<< Updated upstream
        call, id=id
=======
        call, id=id, i=i, id2=id2
>>>>>>> Stashed changes
    )