# -*- coding: utf-8 -*-
"""
STX Lunch server.
"""
from .main import app, db, init

from . import views
from . import models

from .utils import get_current_date, get_current_datetime, make_date, get_current_month, get_current_year
app.jinja_env.globals["get_current_date"] = get_current_date
app.jinja_env.globals["get_current_datetime"] = get_current_datetime
app.jinja_env.globals["make_date"] = make_date
app.jinja_env.globals["get_current_month"] = get_current_month
app.jinja_env.globals["get_current_year"] = get_current_year
