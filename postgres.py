from models import User, db, data, Letter


async def startup():
    await db.set_bind(data.host)
    await db.gino.create_all()



async def get_users(a=10):
    #users = await User.query.gino.all()
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

async def create_user(tg_id):
    user = await User.create(tg_id=tg_id)

async def get_letter(id):
    letter = await Letter.query.where(Letter.id == id).gino.first()
    return letter




