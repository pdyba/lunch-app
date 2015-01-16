# -*- coding: utf-8 -*-
"""
STX Lunch server.
"""
# pylint: disable=missing-docstring

from .main import app, db, init

from . import views
from . import models
