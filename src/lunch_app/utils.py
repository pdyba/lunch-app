# -*- coding: utf-8 -*-
"""
helper functions for jinjna.
"""
import datetime

from flask import flash, request
from flask.ext.mail import Message

from sqlalchemy import and_

from .main import mail, db
from .models import Order, MailText, Food, OrderingInfo
from .models import User
from .webcrawler import get_dania_dnia_from_pod_koziolek, \
    get_week_from_tomas_crawler


def get_current_datetime():
    """
    Returns current datetime as datetime type for jinjna.
    """
    return datetime.datetime.today()


def get_current_date():
    """
    Returns current date as date type for jinjna.
    """
    return datetime.date.today()


def get_current_month():
    """
    Returns current date as date type for jinjna.
    """
    date = datetime.date.today()
    return date.month


def get_current_year():
    """
    Returns current date as date type for jinjna.
    """
    date = datetime.date.today()
    return date.year


def make_date(new_date):
    """
    Converts datetime to date type for jinjna.
    """
    return new_date.date()


def make_datetime(new_date):
    """
    Converts date to datetime type for jinjna.
    """
    date = datetime.datetime.combine(new_date, datetime.time(0, 0))
    return date


def next_month(year, month):
    """
    Returns next month
    2015, 12 -> 2016, 01
    """
    if month + 1 == 13:
        year += 1
        month = 1
    else:
        month += 1
    return year, month


def previous_month(year, month):
    """
    Retruns Previous month
    2015, 01 -> 2014, 12
    """
    if month - 1 == 0:
        year -= 1
        month = 12
    else:
        month -= 1
    return year, month


def ordering_is_active():
    """
    Returns value true if ordering is active for jinja.
    """
    ordering_is_allowed = OrderingInfo.query.get(1)
    return ordering_is_allowed.is_allowed


def server_url():
    """
    Returns current server url.
    """
    url = str(request.url_root).rstrip('/')
    return url


def send_daily_reminder():
    """
    Sends daily reminder to all users function.
    """
    day = datetime.date.today()
    today_beg = datetime.datetime.combine(day, datetime.time(00, 00))
    today_end = datetime.datetime.combine(day, datetime.time(23, 59))
    orders = Order.query.filter(
        and_(
            Order.date >= today_beg,
            Order.date <= today_end,
        )
    ).all()
    users = User.query.filter(
        and_(
            User.i_want_daily_reminder,
            User.active
        )
    ).all()
    message_text = MailText.query.first()
    order_list = ([order.user_name for order in orders])
    emails = ([user.username for user in users
               if user.username not in order_list])
    msg = Message(
        '{} {}'.format(
            message_text.daily_reminder_subject,
            datetime.date.today()
        ),
        recipients=emails,
    )
    msg.body = message_text.daily_reminder
    mail.send(msg)


def add_daily_koziolek():
    """
    Adds meal of a day from pod koziolek
    """
    food = get_dania_dnia_from_pod_koziolek()
    for category in food:
        for meal in food[category]:
            new_meal = Food()
            new_meal.cost = 2 if category == 'zupy' else 11
            new_meal.description = "Danie dnia Koziołek: {}".format(meal)
            new_meal.company = "Pod Koziołkiem"
            new_meal.o_type = "daniednia"
            new_meal.date_available_from = datetime.date.today()
            new_meal.date_available_to = datetime.date.today()
            db.session.add(new_meal)
    db.session.commit()


def get_week_from_tomas():
    """
    Adds weak meals from Tomas ! use only on mondays ! - function
    """
    foods = get_week_from_tomas_crawler()
    for meal in foods['diet']:
        new_meal = Food()
        new_meal.cost = 12
        new_meal.description = meal
        new_meal.company = "Tomas"
        new_meal.o_type = "tygodniowe"
        new_meal.date_available_from = datetime.date.today()
        new_meal.date_available_to = \
            datetime.date.today() + \
            datetime.timedelta(days=4)
        db.session.add(new_meal)
    for i in range(1, 6):
        food = foods['dzien_{}'.format(i)]
        day_diff = datetime.date.today() + datetime.timedelta(days=i-1)
        for meal in food['zupy']:
            new_meal = Food()
            new_meal.cost = 4
            new_meal.description = meal
            new_meal.company = "Tomas"
            new_meal.o_type = "daniednia"
            new_meal.date_available_from = day_diff
            new_meal.date_available_to = day_diff
            db.session.add(new_meal)
        for meal in food['dania']:
            new_meal = Food()
            new_meal.cost = 10
            new_meal.description = meal
            new_meal.company = "Tomas"
            new_meal.o_type = "daniednia"
            new_meal.date_available_from = day_diff
            new_meal.date_available_to = day_diff
            db.session.add(new_meal)
        for meal in food['zupa_i_dania']:
            new_meal = Food()
            new_meal.cost = 12
            new_meal.description = meal
            new_meal.company = "Tomas"
            new_meal.o_type = "daniednia"
            new_meal.date_available_from = day_diff
            new_meal.date_available_to = day_diff
            db.session.add(new_meal)
    db.session.commit()
