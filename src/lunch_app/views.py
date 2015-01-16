# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
"""
Defines views.
"""
from flask import redirect, render_template, url_for, request, flash
from flask.ext import login

from lunch_app.main import app, db
from lunch_app.forms import OrderForm
from lunch_app.models import Order

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


@app.route('/order', methods=['GET', 'POST'])
def create_order():
    form = OrderForm(request.form)
    if request.method == 'POST' and form.validate():
        order = Order()
        form.populate_obj(order)
        db.session.add(order)
        db.session.commit()
        flash('Order Accepted')
        if form.send_me_a_copy:
            """
            kod wysylajacy email
            email backend ?
            """
            pass
        return redirect('/')
    return render_template('order.html', form=form)

