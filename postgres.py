from aiogram import types

from models import User, db, data, Letter, Answer


async def startup():
    await db.set_bind(data.host)
    await db.gino.create_all()



async def get_users(a=10):

    users = []
    async with db.transaction():
        async for row in User.select('id', 'tg_id', 'username', 'firstname', 'lastname', 'fullname', 'is_blocked_by_bot',
                                     'is_bot_blocked', 'language', 'is_admin').gino.iterate():

            if a == 10:
                users.append(row)
            else:
                users.append(row[a])

    return users


async def get_user(id):
    user = await User.query.where(User.id == id).gino.first()
    return user

async def count_users():
    return await db.func.count(User.id).gino.scalar()

async def count_bot_blocked_users():
    return (await db.select([db.func.count()]).where(User.is_bot_blocked==True).gino.scalar())

async def count_blocked_by_bot_users():
    return (await db.select([db.func.count()]).where(User.is_blocked_by_bot==True).gino.scalar())

async def count_admin_users():
    return (await db.select([db.func.count()]).where(User.is_admin==True).gino.scalar())

async def count_letters():
    return await db.func.count(Letter.id).gino.scalar()

async def count_delivered_letters():
    return (await db.select([db.func.count()]).where(Letter.status=="DELIVERED").gino.scalar())

async def count_checking_letters():
    return (await db.select([db.func.count()]).where(Letter.status=="CHECKING").gino.scalar())

async def count_error_letters():
    return (await db.select([db.func.count()]).where(Letter.status=="ERROR").gino.scalar())

async def count_rejected_letters():
    return (await db.select([db.func.count()]).where(Letter.status=="REJECTED").gino.scalar())

async def count_approved_letters():
    return (await db.select([db.func.count()]).where(Letter.status=="APPROVED").gino.scalar())

async def count_creating_letters():
    return (await db.select([db.func.count()]).where(Letter.status=="CREATING").gino.scalar())

async def count_sending_answers():
    return (await db.select([db.func.count()]).where(Answer.status=="SENDING").gino.scalar())

async def count_error_answers():
    return (await db.select([db.func.count()]).where(Answer.status=="ERROR").gino.scalar())

async def count_delivered_answers():
    return (await db.select([db.func.count()]).where(Answer.status=="DELIVERED").gino.scalar())

async def count_answers():
    return await db.func.count(Answer.id).gino.scalar()

async def get_user_by_tg_id(tg_id):
    user = await User.query.where(User.tg_id == tg_id).gino.first()
    return user

async def get_user_by_username(username):
    user = await User.query.where(User.username == username).gino.first()
    return user

async def create_user(user):
    user = types.User.get_current()
    tg_id = user.id
    first_name = user.first_name
    last_name = user.last_name
    full_name = user.full_name
    language = user.locale.language
    username = user.username
    is_blocked_by_bot = False
    is_bot_blocked = False
    is_admin = False
    user = await User.create(tg_id=tg_id, firstname=first_name, lastname = last_name, fullname=full_name,
                       username=username, is_blocked_by_bot=is_blocked_by_bot,
                       is_bot_blocked=is_bot_blocked,
                       language=language, is_admin=is_admin)
    return user

async def get_letter(id):
    letter = await Letter.query.where(Letter.id == id).gino.first()
    return letter

async def get_answer(id):
    answer = await Answer.query.where(Answer.id == id).gino.first()
    return answer

async def get_answer_by_recipient_message_id(id):
    print(id)
    answer = await Answer.query.where(Answer.recipient_message_id == id).gino.first()
    return answer

async def get_file_id(answer, reply_to_message):


    if answer.type == "PHOTO":
        file_id = reply_to_message.photo.file_id
    elif answer.type == 'VIDEO':
        file_id = reply_to_message.video.file_id
    elif answer.type == 'ANIMATION':
        file_id = reply_to_message.animation.file_id
    elif answer.type == 'STICKER':
        file_id = reply_to_message.sticker.file_id
    elif answer.type == 'VOICE':
        file_id = reply_to_message.voice.file_id
    elif answer.type == 'VIDEO_NOTE':
        file_id = reply_to_message.video_note.file_id
    elif answer.type == 'AUDIO':
        file_id = reply_to_message.audio.file_id
    elif answer.type == 'TEXT':
        file_id = reply_to_message.message_id
    else:
        file_id = "error"
    return file_id



