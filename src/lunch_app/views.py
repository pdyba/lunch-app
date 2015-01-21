# -*- coding: utf-8 -*-

"""
Defines views.
"""
import datetime

from flask import redirect, render_template, request, flash
from flask.ext import login
from flask.ext.login import current_user
from sqlalchemy import and_


from .main import app, db
from .forms import OrderForm, AddFood
from .models import Order, Food
from .permissions import user_is_admin


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
@login.login_required
def create_order():
    """
    Create new order page.
    """
    form = OrderForm(request.form)
    day = datetime.date.today()
    today_from = datetime.datetime.combine(day, datetime.time(23, 59))
    today_to = datetime.datetime.combine(day, datetime.time(0, 0))
    food = Food.query.filter(
        and_(
            Food.date_available_from <= today_from,
            Food.date_available_to >= today_to,
        )
    ).all()
    food_list = [(" ", " ")]
    for meal in food:
        label = "{meal.company} " \
                " | {meal.cost} pln | " \
                "{meal.description}".format(meal=meal)
        food_list.append((label, label))
    form.meal_from_list.choices = food_list
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
@user_is_admin
def add_food():
    """
    Add new food page.
    """
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
@user_is_admin
def day_summary():
    """
    Day orders summary.
    """
    day = datetime.date.today()
    today = datetime.datetime.combine(day, datetime.time(00, 00))
    orders_t_12 = Order.query.filter(
        and_(
            Order.date == today,
            Order.company == 'Tomas',
            Order.arrival_time == '12:00'
        )
    ).all()
    orders_t_13 = Order.query.filter(
        and_(
            Order.date == today,
            Order.company == 'Tomas',
            Order.arrival_time == '13:00'
        )
    ).all()
    orders_pk_12 = Order.query.filter(
        and_(
            Order.date == today,
            Order.company == 'Pod Koziołkiem',
            Order.arrival_time == '12:00'
        )
    ).all()
    orders_pk_13 = Order.query.filter(
        and_(
            Order.date == today,
            Order.company == 'Pod Koziołkiem',
            Order.arrival_time == '13:00'
        )
    ).all()
    return render_template(
        'day_summary.html',
        orders_t_12=orders_t_12,
        orders_t_13=orders_t_13,
        orders_pk_12=orders_pk_12,
        orders_pk_13=orders_pk_13,
    )


@app.route('/my_orders', methods=['GET', 'POST'])
@login.login_required
def my_orders():
    orders = Order.query.filter_by(user_name=current_user.username).all()
    return render_template('my_orders.html', orders=orders)


@app.route('/info', methods=['GET', 'POST'])
@login.login_required
def info():
    return render_template('info.html')
