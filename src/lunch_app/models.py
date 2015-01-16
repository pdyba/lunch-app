# pylint: disable=missing-docstring
from datetime import datetime

from flask.ext.login import UserMixin
from flask.ext.sqlalchemy import BaseQuery
from sqlalchemy import Column, Integer, String, Boolean, Unicode, DateTime
from lunch_app import db


class CategoryQuery(BaseQuery):

    def getall(self):
        return self.all()

    def getcategory_id(self, id):
        return self.get(id)

class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = Column(Integer, autoincrement=True, primary_key=True)
    active = Column(Boolean, default=True)
    email = Column(String(200))
    name = Column(Unicode(40), index=True)
    password = Column(String(200), default='')
    username = Column(String(200))
    admin = Column(Boolean, default=True)

    def is_active(self):
        return self.active

    def is_admin(self):
        return self.admin


class Order(db.Model):
    __tablename__ = 'order'
    id = Column(Integer, primary_key=True)
    description = Column(String(800), unique=False)
    cost = Column(Integer)
    arrival_time = Column(Integer)
    company = Column(Integer)
    date = Column(DateTime)

    def __init__(
            self,
            description=None,
            cost=None,
            arrival_time=None,
            company=None,
            date=None):
        self.description = description
        self.cost = cost
        self.arrival_time = arrival_time
        self.company = company
        if date is None:
            date = datetime.today()

    def __repr__(self):
        return '<Order %r>' % (self.id)


class FoodQuery(BaseQuery):

    def getall(self):
        return self.all()

    def getcomment_id(self, id):
        return self.get(id)


class Food(db.Model):
    id = Column(Integer, primary_key=True)
    query_class = FoodQuery
    company = Column(String(80), unique=False)
    description = Column(String(800), unique=False)
    cost = Column(Integer)
    date_available = Column(DateTime)
    date_avalible_upto = Column(DateTime)


