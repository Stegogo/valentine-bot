from gino import Gino
import asyncio
import data

db = Gino()

class User(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.Unicode(), default='noname')
    message_for_user = db.Column(db.Unicode(), default='Empty')


async def main():
    await db.set_bind(data.host)
    await db.gino.create_all()

    # further code goes here

    await db.pop_bind().close()


asyncio.get_event_loop().run_until_complete(main())

