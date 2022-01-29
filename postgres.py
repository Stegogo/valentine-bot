from gino import Gino
import asyncio
import data

db = Gino()

class User(db.Model):
    __tablename__ = 'messages'

    id = Column(db.Integer, Sequence("user_id_seq"), primary_key=True)
    tg_id = Column(db.Integer)
    username = Column(db.String(200))
    firstname = Column(db.String(200))
    lastname = Column(db.String(200))
    fullname = Column(db.String(200))
    is_blocked_by_bot = Column(db.Boolean)
    is_bot_blocked = Column(db.Boolean)
    language = Column(db.String(200))
    is_admin = Column(db.Boolean)



async def main():
    await db.set_bind(data.host)
    await db.gino.create_all()
    '''

    async def create(id, username, username_type, message_for_user):
        user = await User.create(id=id,username=username, username_type=username_type, message_for_user=message_for_user)

    await create(id, username, username_type, message_for_user)
'''
    s = []
    async with db.transaction():
        async for row in User.select('id', 'username', 'username_type', 'message_for_user').gino.iterate():
            s.append(row[0])



    # further code goes here

    await db.pop_bind().close()
    return s


async def get_users():
    users = await User.query.gino.all()
    return users

async def get_user(id):
    user = await User.query.where(User.id == id).gino.first()
    return user


