from gino import Gino
import asyncio
import data

db = Gino()

class User(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.Unicode(), default='empty')
    username_type = db.Column(db.Unicode(), default='empty')
    message_for_user = db.Column(db.Unicode(), default='empty')



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

async def create(id):
    await db.set_bind(data.host)
    user = await User.create(id=id)


asyncio.get_event_loop().run_until_complete(main())

