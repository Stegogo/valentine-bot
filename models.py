from gino import Gino
import data

db = Gino()

class User(db.Model):
    __tablename__ = 'users'

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

