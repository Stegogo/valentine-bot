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
    query: sql.Select

    id = Column(db.Integer, Sequence("letters_id_seq"), primary_key=True)
    sender_id= Column(db.Integer)
    recipient_id=Column(db.Integer)
    status = Column(db.String)
    text = Column(db.String)
    recipient_username = Column(db.String)
    recipient_phone_number = Column(db.String)
    type = Column(db.String)
    file_id_bot = Column(db.String)
    file_id_userbot = Column(db.String)
    sender_message_id =Column(db.Integer)
    recipient_message_id = Column(db.Integer)
    link_preview = Column(db.Boolean)
    recipient_fullname = Column(db.String)
    reject_reason = Column(db.String)
    admin_message_id = Column(db.Integer)