# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
"""
Defines views.
"""
from functools import wraps

from flask import redirect, render_template, url_for, request, flash
from flask.ext import login
from flask.ext.login import current_user


from .main import app, db
from .forms import OrderForm, AddFood
from .models import Order, Food, User
from sqlalchemy.orm import session, aliased, query

import logging
log = logging.getLogger(__name__)  # pylint: disable=invalid-name


def user_is_admin(user):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if user:
                if not user.is_admin():
                    flash("You shell not pass")
                    return redirect('order')
                else:
                    return f(*args, **kwargs)
        return wrapped
    return wrapper


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
@login.login_required
def create_order():
    form = OrderForm(request.form)
    food = Food.query.all()

    # meal = food[0]
    # print('\n\n\n', meal, '\n\n\n')
    # meals = []
    # for m in meal:
    #     meals.append(m)
    # form.food.choices = meals
    # print('\n\n\n', meals, '\n\n\n')
    if request.method == 'POST' and form.validate():
        order = Order()
        form.populate_obj(order)
        user_name = current_user.username

        order.user_name = user_name
        db.session.add(order)
        db.session.commit()
        flash('Order Accepted')
        if form.send_me_a_copy:
            # TODO define email backend and e_mail
            pass
        return redirect('order')
    return render_template('order.html', form=form, food=food)


@app.route('/add_food', methods=['GET', 'POST'])
@login.login_required
@user_is_admin(current_user)
def add_food():
    form = AddFood(request.form)
    if request.method == 'POST' and form.validate():
        food = Food()
        form.populate_obj(food)
        db.session.add(food)
        db.session.commit()
        flash('Food Created')
        return redirect('add_food')
    return render_template('add_food.html', form=form)


@app.route('/day_summary', methods=['GET', 'POST'])
@login.login_required
@user_is_admin(current_user)
def day_summary():
    orders = Order.query.all()
    return render_template('day_summary.html', orders=orders)


@app.route('/my_orders', methods=['GET', 'POST'])
@login.login_required
def my_orders():
    orders = Order.query.filter_by(user_name=current_user.username).all()
    return render_template('my_orders.html', orders=orders)
