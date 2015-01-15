# -*- coding: utf-8 -*-
"""
Defines views.
"""
from flask import redirect, render_template, url_for
from flask.ext import login

from lunch_app.main import app

import logging
log = logging.getLogger(__name__)  # pylint: disable=invalid-name


@app.route('/')
def index():
    """
    Main page.
    """
    return render_template('index.html')


@app.route('/overview')
@login.login_required
def overview():
    """
    Overview page.
    """
    return render_template('overview.html')
