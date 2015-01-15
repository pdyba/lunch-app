# -*- coding: utf-8 -*-
"""
Defines views.
"""
from flask import redirect, render_template, url_for
from flask.ext import login

from lunch_app.main import app
from lunch_app.forms import OrderForm

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

@app.route('/order')
def create_order():
    form = OrderForm.order_form()
    return render_template('order.html', form=form)
