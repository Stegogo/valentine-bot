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


class Letter(db.Model):
    __tablename__ = "letters"

    id = db.Column(db.Integer, db.Sequence("letters_id_seq"), primary_key=True)
    photo = db.Column(db.String)
    video = db.Column(db.String)
    sender_id = db.Column(db.Integer)
    recipient_id = db.Column(db.Integer)
    status = db.Column(db.String)
    text = db.Column(db.String)
    photo = db.Column(db.String)
    recipient_username = db.Column(db.String)
    recipient_phone_number = db.Column(db.String)
    type = db.Column(db.String)
    file_id_bot = db.Column(db.String)
    file_id_userbot = db.Column(db.String)
    sender_message_id = db.Column(db.Integer)
    recipient_message_id = db.Column(db.Integer)
    link_preview = db.Column(db.Boolean)
    recipient_fullname = db.Column(db.String)
    reject_reason = db.Column(db.String)
    admin_message_id = db.Column(db.Integer)

