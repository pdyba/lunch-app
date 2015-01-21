"""
models for lunch app db.
"""
from datetime import datetime

from flask.ext.login import UserMixin

from sqlalchemy import Column, Integer, String, Boolean, Unicode, DateTime

from .main import db


class User(db.Model, UserMixin):
    """
    User model for lunch app db.
    """
    __tablename__ = 'user'
    id = Column(Integer, autoincrement=True, primary_key=True)
    active = Column(Boolean, default=True)
    email = Column(String(200))
    name = Column(Unicode(40), index=True)
    password = Column(String(200), default='')
    username = Column(String(200))
    admin = Column(Boolean, default=False)

    def is_active(self):
        """
        Returns if Users is active.
        """
        return self.active

    def is_admin(self):
        """
        Returns if Users is admin.
        """
        return self.admin


class Order(db.Model):
    """
    Order model for lunch app db.
    """
    __tablename__ = 'order'
    id = Column(Integer, primary_key=True)
    meal_from_list = Column(String(200), unique=False)
    description = Column(String(800), unique=False)
    cost = Column(Integer)
    arrival_time = Column(Integer)
    company = Column(Integer)
    date = Column(DateTime)
    user_name = Column(String(80), db.ForeignKey('user.name'))

    def __init__(
            self,
            description=None,
            cost=None,
            arrival_time=None,
            company=None,
            date=None):
        """
        Inits orders db.
        """
        self.description = description
        self.cost = cost
        self.arrival_time = arrival_time
        self.company = company
        if self.date is None:
            self.date = datetime.today()

    def __repr__(self):
        """
        Returns orders id.
        """
        return '<Order %r>' % self.id


class Food(db.Model):
    """
    Food model for lunch app db.
    """
    __tablename__ = 'food'
    id = Column(Integer, primary_key=True)
    company = Column(String(80), unique=False)
    description = Column(String(800), unique=False)
    cost = Column(Integer)
    date_available_from = Column(DateTime)
    date_available_to = Column(DateTime)
