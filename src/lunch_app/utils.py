import datetime


def get_current_datetime():
    return datetime.datetime.today()


def get_current_date():
    return datetime.date.today()


def make_date(new_date):
    return new_date.date()
