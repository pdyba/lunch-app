# -*- coding: utf-8 -*-
"""
helper functions for jinjna.
"""
import datetime

from flask import current_app, request, render_template, redirect
from social.exceptions import SocialAuthBaseException
from werkzeug.exceptions import HTTPException


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


def error_handler(error):
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
        name = "WTF"
    return render_template(
        'error.html',
        code=code,
        description=description,
        name=name,
        msg=msg,
    )
