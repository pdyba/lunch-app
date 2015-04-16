# -*- coding: utf-8 -*-
# pylint: disable=invalid-name, no-member
"""
Helper functions.
"""
from calendar import monthrange
import datetime

from flask import current_app, request, render_template, redirect
from social.exceptions import SocialAuthBaseException
from sqlalchemy import and_
from werkzeug.exceptions import HTTPException
from flask.ext.mail import Message

from .webcrawler import get_dania_dnia_from_pod_koziolek, \
    get_week_from_tomas_crawler


def db_session_commit():
    """
    Commits changes to database.
    """
    from .main import db

    db.session.commit()


def get_current_datetime():
    """
    Returns current datetime as datetime type for jinja.
    """
    return datetime.datetime.today()


def get_current_date():
    """
    Returns current date as date type for jinja.
    """
    return datetime.date.today()


def get_current_month():
    """
    Returns current date as date type for jinja.
    """
    date = datetime.date.today()
    return date.month


def get_current_year():
    """
    Returns current date as date type for jinja.
    """
    date = datetime.date.today()
    return date.year


def make_date(new_date):
    """
    Converts datetime to date type for jinja.
    """
    return new_date.date()


def make_datetime(new_date):
    """
    Converts date to datetime type for jinja.
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


def error_handler(error):
    """
    Error handler for the app and google API login.
    """
    msg = "Request resulted in {}".format(error)
    from .main import app
    if not app.config.get('TESTING', False):
        current_app.logger.warning(msg, exc_info=error)

    if isinstance(error, SocialAuthBaseException):
        return redirect('/YouAreNotAHero')
    elif isinstance(error, HTTPException):
        description = error.get_description(request.environ)
        code = error.code
        name = error.name
    else:
        description = ("We encountered an error "
                       "while trying to fulfill your request")
        code = 500
        name = "Unknown and unexpected error"
    return render_template(
        'error.html',
        code=code,
        description=description,
        name=name,
        msg=msg,
    )


def ordering_is_active():
    """
    Returns value true if ordering is active for jinja.
    """
    from .models import OrderingInfo

    ordering_is_allowed = OrderingInfo.query.get(1)
    return ordering_is_allowed.is_allowed


def server_url():
    """
    Returns current server url.
    """
    url = str(request.url_root).rstrip('/')
    return url


def current_day_orders():
    """
    Returns all orders for current day.
    """
    from .models import Order

    day = datetime.date.today()
    today_beg = datetime.datetime.combine(day, datetime.time(00, 00))
    today_end = datetime.datetime.combine(day, datetime.time(23, 59))
    return Order.query.filter(
        and_(
            Order.date >= today_beg,
            Order.date <= today_end,
        )
    ).all()


def add_a_new_meal(price, meal, date_from, date_to, comp, type="daniednia"):
    """
    Adds a new meal to menu
    """
    from .models import Food
    from .main import db

    db.session.add(
        Food(
            cost=price,
            description=meal,
            company=comp,
            o_type=type,
            date_available_from=date_from,
            date_available_to=date_to,
        )
    )


def send_daily_reminder():
    """
    Sends daily reminder to all users function.
    """
    from .models import MailText, User
    from .main import mail

    orders = current_day_orders()
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
            cost = 2 if category == 'zupy' else 11
            add_a_new_meal(
                cost,
                "Danie dnia Koziołek: {}".format(meal),
                datetime.date.today(),
                datetime.date.today(),
                "Pod Koziołkiem",
                type="daniednia",
            )

    db_session_commit()


def get_week_from_tomas():
    """
    Adds weak meals from Tomas ! use only on mondays ! - function
    """
    foods = get_week_from_tomas_crawler()
    for meal in foods['diet']:
        add_a_new_meal(
            12,
            meal,
            datetime.date.today(),
            datetime.date.today() + datetime.timedelta(days=4),
            "Tomas",
            type="tygodniowe"
        )
    for i in range(1, 6):
        food = foods['dzien_{}'.format(i)]
        day_diff = datetime.date.today() + datetime.timedelta(days=i-1)
        for meal in food['zupy']:
            add_a_new_meal(4, meal, day_diff, day_diff, "Tomas")
        for meal in food['dania']:
            add_a_new_meal(10, meal, day_diff, day_diff, "Tomas")
        for meal in food['zupa_i_dania']:
            add_a_new_meal(12, meal, day_diff, day_diff, "Tomas")
    db_session_commit()


def current_day_meals():
    """
    Gets meals from current day.
    """
    from .models import Food
    day = datetime.date.today()
    today_from = datetime.datetime.combine(day, datetime.time(23, 59))
    today_to = datetime.datetime.combine(day, datetime.time(0, 0))
    foods = Food.query.filter(
        and_(
            Food.date_available_from <= today_from,
            Food.date_available_to >= today_to,
        )
    ).all()
    return foods


def current_day_meals_and_companies(companies):
    """
    Gets meals from current day, and companies for daily and manu.
    """
    foods = current_day_meals()
    companies_current = [
        company
        for company in companies
        if any([
            meal.company == company.name
            for meal in foods
            if meal.o_type != 'menu'
        ])
    ]
    companies_menu = [
        company
        for company in companies
        if any([
            meal.company == company.name
            for meal in foods
            if meal.o_type == 'menu'
        ])
    ]
    return foods, companies_current, companies_menu


def month_orders(year, month, user=None):
    """
    Gets meals from current day, and companies for daily and manu.
    """
    from .models import Order

    month_begin = datetime.datetime(
        year=year,
        month=month,
        day=1,
        hour=0,
        minute=0,
        second=1
    )
    day = monthrange(year, month)[1]
    month_end = datetime.datetime(
        year=year,
        month=month,
        day=day,
        hour=23,
        minute=59,
        second=59
    )
    if user:
        return Order.query.filter(
            and_(
                Order.date >= month_begin,
                Order.date <= month_end,
                Order.user_name == user,
            )
        ).all()
    return Order.query.filter(
        and_(
            Order.date >= month_begin,
            Order.date <= month_end,
        )
    ).all()


def change_ordering_status(block_or_not):
    """
    Allows to block or unblock ordering for everyone.
    """
    from .models import OrderingInfo
    OrderingInfo.query.get(1).is_allowed = block_or_not
    db_session_commit()


def get_conflicts_amount(user):
    """
    Get current conflicts number.
    """
    from sqlalchemy import or_
    from .models import Conflict

    if user.is_admin():
        return len(Conflict.query.filter(
            and_(
                Conflict.resolved == False,
                or_(
                    Conflict.created_by_user == user.username,
                    Conflict.user_connected == user.username,
                ),
            )
        ).all())
    else:
        return len(Conflict.query.filter(Conflict.resolved == False).all())

