# -*- coding: utf-8 -*-
# pylint: disable=invalid-name, no-member
"""
Defines views.
"""
import datetime
from calendar import monthrange, month_name

from flask import redirect, render_template, request, flash, url_for
from flask.ext import login
from flask.ext.login import current_user
from flask.ext.mail import Mail, Message
from sqlalchemy import and_

from .main import app, db
from .forms import OrderForm, AddFood, OrderEditFrom, UserOrders, CompanyOrders
from .models import Order, Food, User
from .permissions import user_is_admin

import logging

log = logging.getLogger(__name__)
mail = Mail(app)


@app.route('/')
def index():
    """
    Main page.
    """
    if not current_user.is_anonymous():
        return redirect('order')
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
    if request.method == 'POST' and form.validate():
        order = Order()
        form.populate_obj(order)
        user_name = current_user.username
        order.user_name = user_name

        db.session.add(order)
        db.session.commit()
        flash('Order Accepted')
        if form.send_me_a_copy.data:
            msg = Message(
                'STXNext Lunch App Your Order '
                '{date}'.format(date=datetime.date.today()),
                sender='piotr.dyba@stxnext.pl',
                recipients=[current_user.email],
            )
            msg.body = "Your today order is: \n {order.description} \n " \
                       "from {order.company} it cost {order.cost}zl and will " \
                       "come at {order.arrival_time}".format(order=order)
            mail.send(msg)
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
    today_beg = datetime.datetime.combine(day, datetime.time(00, 00))
    today_end = datetime.datetime.combine(day, datetime.time(23, 59))

    orders_t_12 = Order.query.filter(
        and_(
            Order.date >= today_beg,
            Order.date <= today_end,
            Order.company == 'Tomas',
            Order.arrival_time == '12:00'
        )
    ).all()
    orders_t_12_cost = 0
    for order in orders_t_12:
        orders_t_12_cost += order.cost

    orders_t_13 = Order.query.filter(
        and_(
            Order.date >= today_beg,
            Order.date <= today_end,
            Order.company == 'Tomas',
            Order.arrival_time == '13:00'
        )
    ).all()
    orders_t_13_cost = 0
    for order in orders_t_13:
        orders_t_13_cost += order.cost

    orders_pk_12 = Order.query.filter(
        and_(
            Order.date >= today_beg,
            Order.date <= today_end,
            Order.company == 'Pod Koziołkiem',
            Order.arrival_time == '12:00'
        )
    ).all()
    orders_pk_12_cost = 0
    for order in orders_pk_12:
        orders_pk_12_cost += order.cost

    orders_pk_13 = Order.query.filter(
        and_(
            Order.date >= today_beg,
            Order.date <= today_end,
            Order.company == 'Pod Koziołkiem',
            Order.arrival_time == '13:00'
        )
    ).all()
    orders_pk_13_cost = 0
    for order in orders_pk_13:
        orders_pk_13_cost += order.cost

    return render_template(
        'day_summary.html',
        orders_t_12=orders_t_12,
        orders_t_12_cost=orders_t_12_cost,
        orders_t_13=orders_t_13,
        orders_t_13_cost=orders_t_13_cost,
        orders_pk_12=orders_pk_12,
        orders_pk_12_cost=orders_pk_12_cost,
        orders_pk_13=orders_pk_13,
        orders_pk_13_cost=orders_pk_13_cost,
    )


@app.route('/my_orders', methods=['GET', 'POST'])
@login.login_required
def my_orders():
    """
    Renders all of current user orders.
    """
    orders = Order.query.filter_by(user_name=current_user.username).all()
    orders_cost = 0
    for order in orders:
        orders_cost += order.cost
    return render_template(
        'my_orders.html',
        orders=orders,
        orders_cost=orders_cost,
    )


@app.route('/info', methods=['GET', 'POST'])
@login.login_required
def info():
    """
    Renders info page.
    """
    return render_template('info.html')


@app.route('/order_details/<int:order_id>', methods=['GET', 'POST'])
@login.login_required
def order_details(order_id):
    """
    Renders orders detail page.
    """
    order = Order.query.filter(Order.id == order_id).first()
    return render_template('order_details.html', order=order)


@app.route('/order_edit/<int:order_id>/', methods=['GET', 'POST'])
@login.login_required
@user_is_admin
def edit_order(order_id):
    """
    Renders order edit page.
    """
    order = Order.query.filter(Order.id == order_id).first()
    form = OrderEditFrom(obj=order)
    if request.method == 'POST' and form.validate():
        form.populate_obj(order)
        db.session.add(order)
        db.session.commit()
        flash('Order Edited')
        return redirect('day_summary')
    return render_template('order_edit.html', form=form)


@app.route('/order_list', methods=['GET', 'POST'])
@login.login_required
def order_list():
    """
    Renders order list page form.
    """
    form = UserOrders(request.form)
    users = User.query.all()
    user_list = []
    for user in users:
        user_list.append((user.id, user.username))
    form.user.choices = user_list
    if request.method == 'POST' and form.validate():
        if form.data['month']:
            return redirect(url_for(
                'order_list_month_view',
                user_id=form.user.data,
                year=form.data['year'],
                month=form.data['month'],
            ))
        else:
            return redirect(url_for(
                'order_list_year_view',
                user_id=form.user.data,
                year=form.data['year'],
                ))
    return render_template('orders_list.html', form=form)


@app.route('/order_list/<int:user_id>/<int:year>', methods=['GET', 'POST'])
@login.login_required
def order_list_year_view(year, user_id):
    """
    Renders order year list page.
    """
    year_begin = datetime.datetime(
        year=year,
        month=1,
        day=1,
        hour=0,
        minute=0,
        second=1
    )
    year_end = datetime.datetime(
        year=year,
        month=12,
        day=31,
        hour=23,
        minute=59,
        second=59
    )
    user = User.query.filter(User.id == user_id).first()
    orders = Order.query.filter(
        and_(
            Order.date >= year_begin,
            Order.date <= year_end,
            Order.user_name == user.username,
        )
    ).all()
    year_data = []
    for month in range(1, 13):
        monthly_data = {
            'month_name': month_name[month],
            'number of orders': 0,
            'month cost': 0,
        }
        for order in orders:
            month_begin = datetime.datetime(
                year=year,
                month=month,
                day=1,
                hour=0,
                minute=0,
                second=1
            )

            day = monthrange(year, month)[1]
            month_end = datetime.datetime(
                year=year,
                month=month,
                day=day,
                hour=23,
                minute=59,
                second=59
            )
            if month_begin <= order.date <= month_end:
                monthly_data['number of orders'] += 1
                monthly_data['month cost'] += order.cost

        year_data.append(monthly_data)

    return render_template(
        'orders_list_year_view.html',
        year_data=year_data,
        user=user,
        year=year
    )


@app.route('/order_list/<int:user_id>/<int:year>/<int:month>', methods=[
    'GET',
    'POST'
])
@login.login_required
def order_list_month_view(year, month, user_id):
    """
    Renders order month list page.
    """
    month_begin = datetime.datetime(
        year=year,
        month=month,
        day=1,
        hour=0,
        minute=0,
        second=1
    )

    day = monthrange(year, month)[1]
    month_end = datetime.datetime(
        year=year,
        month=month,
        day=day,
        hour=23,
        minute=59,
        second=59
    )
    pub_date = {'year': year, 'month': month_name[month]}
    user = User.query.filter(User.id == user_id).first()
    orders = Order.query.filter(
        and_(
            Order.date >= month_begin,
            Order.date <= month_end,
            Order.user_name == user.username,
        )
    ).all()
    orders_cost = 0
    for order in orders:
        orders_cost += order.cost
    return render_template(
        'orders_list_month_view.html',
        orders=orders,
        orders_cost=orders_cost,
        pub_date=pub_date,
        user=user
    )


@app.route('/company_summary', methods=['GET', 'POST'])
@login.login_required
def company_summary_view():
    """
    Renders company query page form.
    """
    form = CompanyOrders(request.form)
    if request.method == 'POST' and form.validate():
            return redirect(url_for(
                'company_summary_month_view',
                year=form.data['year'],
                month=form.data['month'],
            ))
    return render_template('company_summary.html', form=form)


@app.route('/company_summary/<int:year>/<int:month>', methods=['GET', 'POST'])
@login.login_required
def company_summary_month_view(year, month):
    """
    Renders companies month list page.
    """
    month_begin = datetime.datetime(
        year=year,
        month=month,
        day=1,
        hour=0,
        minute=0,
        second=1
    )

    day = monthrange(year, month)[1]
    month_end = datetime.datetime(
        year=year,
        month=month,
        day=day,
        hour=23,
        minute=59,
        second=59
    )
    pub_date = {'year': year, 'month': month_name[month]}
    orders_tomas = Order.query.filter(
        and_(
            Order.date >= month_begin,
            Order.date <= month_end,
            Order.company == 'Tomas',
        )
    ).all()
    orders_koziol = Order.query.filter(
        and_(
            Order.date >= month_begin,
            Order.date <= month_end,
            Order.company == 'Pod Koziołkiem',
        )
    ).all()
    orders_tomas_cost = 0
    for order in orders_tomas:
        orders_tomas_cost += order.cost
    orders_koziol_cost = 0
    for order in orders_koziol:
        orders_koziol_cost += order.cost
    return render_template(
        'company_summary_month_view.html',
        orders_tomas_cost=orders_tomas_cost,
        orders_koziol_cost=orders_koziol_cost,
        pub_date=pub_date,
    )
