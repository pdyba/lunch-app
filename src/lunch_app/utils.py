# -*- coding: utf-8 -*-
"""
helper functions for jinjna.
"""
import datetime


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


def make_date(new_date):
    """
    Converts datetime to date type for jinjna.
    """
    return new_date.date()
