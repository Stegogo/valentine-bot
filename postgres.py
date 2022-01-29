from gino import Gino
import asyncio
import data

db = Gino()

#Модели пихаем в 1 файл
class User(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, db.Sequence("user_id_seq"), primary_key=True)
    tg_id = db.Column(db.Integer)
    username = db.Column(db.String(200))
    firstname = db.Column(db.String(200))
    lastname = db.Column(db.String(200))
    fullname = db.Column(db.String(200))
    is_blocked_by_bot = db.Column(db.Boolean)
    is_bot_blocked = db.Column(db.Boolean)
    language = db.Column(db.String(200))
    is_admin = db.Column(db.Boolean)

async def main():
    await db.set_bind(data.host)
    await db.gino.create_all()
    '''

    async def create(id, username, username_type, message_for_user):
        user = await User.create(id=id,username=username, username_type=username_type, message_for_user=message_for_user)

    await create(id, username, username_type, message_for_user)
'''
    '''
    s = []
    async with db.transaction():
        async for row in User.select('id', 'username', 'username_type', 'message_for_user').gino.iterate():
            s.append(row[0])



    # further code goes here

    await db.pop_bind().close()
    return s
'''




