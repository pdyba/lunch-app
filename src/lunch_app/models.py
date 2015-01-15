
import datetime

from flask.ext.login import UserMixin

from .main import db


class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    active = db.Column(db.Boolean, default=True)
    email = db.Column(db.String(200))
    name = db.Column(db.Unicode(40), index=True)
    password = db.Column(db.String(200), default='')
    username = db.Column(db.String(200))
    admin = db.Column(db.Boolean, default=True)

    def is_active(self):
        return self.active

    def is_admin(self):
        return self.admin


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(800), unique=False)
    cost = db.Column(db.Integer)
    arrival_time = db.Column(db.Integer)
    company = db.Column(db.Integer)
    send_me_a_copy = db.Column(db.Boolean, default=False)