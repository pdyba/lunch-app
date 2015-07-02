# -*- coding: utf-8 -*-
"""
Models for lunch app db.
"""
# pylint: disable=invalid-name, too-few-public-methods, no-init

from datetime import datetime

from flask.ext.login import UserMixin

from sqlalchemy import Column
from sqlalchemy.types import (
    Integer, String, Boolean,
    Unicode, DateTime, Float,
    Date, PickleType,
)

from sqlalchemy.ext.mutable import MutableDict

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
    username = Column(String(200), unique=True)
    admin = Column(Boolean, default=False)
    i_want_daily_reminder = Column(Boolean, default=False)
    rate_timestamp = Column(Date)
    preferred_arrival_time = Column(String(5), default="12:00")

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

    def is_anonymous(self):
        """
        Returns if Users is active.
        """
        return not self.active


class Order(db.Model):
    """
    Order model for lunch app db.
    """
    __tablename__ = 'order'
    id = Column(Integer, primary_key=True)
    description = Column(String(800), unique=False)
    cost = Column(Float)
    arrival_time = Column(String(5))
    company = Column(String(80))
    date = Column(DateTime, default=datetime.utcnow)
    user_name = Column(String(80), db.ForeignKey('user.username'))

    def __init__(
            self,
            description=None,
            cost=None,
            arrival_time=None,
            company=None):
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
    cost = Column(Float)
    date_available_from = Column(DateTime)
    date_available_to = Column(DateTime)
    o_type = Column(String(100))
    rating = Column(Float)


class Finance(db.Model):
    """
    Finance model - did user paid that month.
    """
    __tablename__ = 'finance'
    id = Column(Integer, primary_key=True)
    user_name = Column(String(80), db.ForeignKey('user.username'))
    month = Column(Integer)
    year = Column(Integer)
    did_user_pay = Column(Boolean, default=False)


class MailText(db.Model):
    """
    Mail text messages data base.
    """
    __tablename__ = 'mail_text_msg'
    id = Column(Integer, primary_key=True)
    daily_reminder = Column(String(800))
    daily_reminder_subject = Column(String(200))
    monthly_pay_summary = Column(String(800))
    pay_reminder = Column(String(800))
    pay_slacker_reminder = Column(String(800))
    info_page_text = Column(String(1600))
    blocked_user_text = Column(String(800))
    ordering_is_blocked_text = Column(String(800))


class OrderingInfo(db.Model):
    """
    Ordering availability control.
    """
    __tablename__ = 'ordering_info'
    id = Column(Integer, primary_key=True)
    is_allowed = Column(Boolean, default=True)


class Pizza(db.Model):
    """
    Pizza ordering.
    """
    __tablename__ = 'pizza'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.utcnow)
    pizza_ordering_is_allowed = Column(Boolean, default=False)
    ordered_pizzas = Column(MutableDict.as_mutable(PickleType))
    users_already_ordered = Column(String(5000))
    who_created = Column(String(100))


class Company(db.Model):
    """
    Companies data base
    """
    __tablename__ = 'companies'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    web_page = Column(String(100))
    address = Column(String(400))
    telephone = Column(String(20))
    date_added = Column(DateTime, default=datetime.utcnow)


class Conflict(db.Model):
    """
    Conflicts data base
    """
    __tablename__ = 'conflicts'
    id = Column(Integer, primary_key=True)
    created_by_user = Column(String(100), db.ForeignKey('user.username'))
    user_connected = Column(String(100), nullable=True)
    order_connected = Column(Integer, db.ForeignKey('order.id'))
    date_added = Column(DateTime, default=datetime.utcnow)
    resolved = Column(Boolean, default=False)
    resolved_by = Column(String(200))
    notes = Column(String(500))
    i_know_who = Column(Boolean, default=False)
    did_order_come = Column(Boolean, default=False)
