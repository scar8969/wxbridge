from flask_sqlalchemy import SQLAlchemy

from .clock import utcnow

db = SQLAlchemy()


class Contact(db.Model):
    __tablename__ = "contacts"
    id = db.Column(db.Integer, primary_key=True)
    wxid = db.Column(db.String(64), unique=True)
    name = db.Column(db.String(128), default="")
    is_group = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=utcnow)


class Message(db.Model):
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True)
    contact_id = db.Column(db.Integer, db.ForeignKey("contacts.id"))
    direction = db.Column(db.String(8), default="in")  # in|out
    text = db.Column(db.Text, default="")
    at = db.Column(db.DateTime, default=utcnow)


class Rule(db.Model):
    __tablename__ = "rules"
    id = db.Column(db.Integer, primary_key=True)
    trigger = db.Column(db.String(128), default="")
    action = db.Column(db.String(16), default="reply")  # reply|api|forward
    params_json = db.Column(db.Text, default="{}")
    enabled = db.Column(db.Integer, default=1)
