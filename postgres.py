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

async def get_user_by_tg_id(tg_id):
    user = await User.query.where(User.tg_id == tg_id).gino.first()
    return user

async def create_user(tg_id):
    user = await User.create(tg_id=tg_id)

async def get_letter(id):
    letter = await Letter.query.where(Letter.id == id).gino.first()
    return letter

async def get_answer(id):
    answer = await Answer.query.where(Answer.id == id).gino.first()
    return answer

async def send_answer():
    pass

async def get_file_id(answer, reply_to_message):


    if answer.type == "PHOTO":
        file_id = reply_to_message.photo.file_id
    elif answer.type == 'VIDEO':
        file_id = reply_to_message.video.file_id
    elif answer.type == 'GIF':
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

    return file_id



