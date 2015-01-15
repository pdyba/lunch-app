
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

    def is_active(self):
        return self.active
