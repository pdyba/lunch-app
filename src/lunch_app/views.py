# -*- coding: utf-8 -*-
# pylint: disable=invalid-name, no-member
"""
Defines views.
"""
from calendar import monthrange, month_name
from collections import Counter
import datetime
from random import choice


from flask import redirect, render_template, request, flash, url_for, Response, \
    jsonify
from flask.ext import login
from flask.ext.login import current_user
from flask.ext.mail import Message
from sqlalchemy import and_
from sqlalchemy.exc import OperationalError

from .main import app, db, mail
from .forms import (
    OrderForm,
    AddFood,
    OrderEditForm,
    UserOrders,
    CompanyOrders,
    MailTextForm,
    UserDailyReminderForm,
    FinanceSearchForm,
    FinanceBlockUserForm,
)
from .models import Order, Food, User, Finance, MailText
from .permissions import user_is_admin
from .utils import next_month, previous_month

from werkzeug.exceptions import BadRequestKeyError

import logging

log = logging.getLogger(__name__)

ORDERING_IS_ACTIVE = True


def ordering_is_active():
    return ORDERING_IS_ACTIVE


@app.route('/')
def index():
    """
    Main page.
    """
    if not current_user.is_anonymous():
        return redirect('order')
    return render_template('index.html')


@app.route('/overview', methods=['GET', 'POST'])
@login.login_required
def overview():
    """
    Overview page.
    """

    user = User.query.filter(User.username == current_user.username).first()
    form = UserDailyReminderForm(formdata=request.form, obj=user)
    if request.method == 'POST' and form.validate():
        user.i_want_daily_reminder = \
            request.form.get('i_want_daily_reminder') == 'y'
        db.session.commit()
        return redirect('overview')
    return render_template('overview.html', form=form, user=user)


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
    foods = Food.query.filter(
        and_(
            Food.date_available_from <= today_from,
            Food.date_available_to >= today_to,
        )
    ).all()
    if request.method == 'POST' and form.validate():
        order = Order()
        form.populate_obj(order)
        user_name = current_user.username
        order.user_name = user_name
        db.session.add(order)
        db.session.commit()
        flash('Order created')
        if form.send_me_a_copy.data:
            msg = Message(
                'Lunch order - {}'.format(datetime.date.today()),
                recipients=[current_user.email],
            )
            msg.body = "Today you ordered {order.description} " \
                       "from {order.company} ({order.cost} PLN).\n" \
                       "It should be delivered at " \
                       "{order.arrival_time}".format(order=order)
            mail.send(msg)
            flash('Mail send')
        return redirect('order')
    print(current_user.username, current_user.active, current_user.is_active(),)
    return render_template('order.html', form=form, foods=foods)


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
        flash('Food added')
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
            Order.arrival_time == '12:00',
        )
    ).all()
    orders_t_12_cost = sum(order.cost for order in orders_t_12)

    orders_t_13 = Order.query.filter(
        and_(
            Order.date >= today_beg,
            Order.date <= today_end,
            Order.company == 'Tomas',
            Order.arrival_time == '13:00',
        )
    ).all()
    orders_t_13_cost = sum(order.cost for order in orders_t_13)

    orders_pk_12 = Order.query.filter(
        and_(
            Order.date >= today_beg,
            Order.date <= today_end,
            Order.company == 'Pod Koziołkiem',
            Order.arrival_time == '12:00',
        )
    ).all()
    orders_pk_12_cost = sum(order.cost for order in orders_pk_12)

    orders_pk_13 = Order.query.filter(
        and_(
            Order.date >= today_beg,
            Order.date <= today_end,
            Order.company == 'Pod Koziołkiem',
            Order.arrival_time == '13:00',
        )
    ).all()
    orders_pk_13_cost = sum(order.cost for order in orders_pk_13)

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
    orders_cost = sum(order.cost for order in orders)
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
    order = Order.query.get(order_id)
    form = OrderEditForm(formdata=request.form, obj=order)
    if request.method == 'POST' and form.validate():
        form.populate_obj(order)
        db.session.commit()
        flash('Order changed')
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
    orders_cost = sum(order.cost for order in orders)
    return render_template(
        'orders_list_month_view.html',
        orders=orders,
        orders_cost=orders_cost,
        pub_date=pub_date,
        user=user
    )


@app.route('/company_summary', methods=['GET', 'POST'])
@login.login_required
@user_is_admin
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
@user_is_admin
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
    orders_tomas_cost = sum(order.cost for order in orders_tomas)
    orders_koziol_cost = sum(order.cost for order in orders_koziol)
    return render_template(
        'company_summary_month_view.html',
        orders_tomas_cost=orders_tomas_cost,
        orders_koziol_cost=orders_koziol_cost,
        pub_date=pub_date,
    )


@app.route('/finance/<int:year>/<int:month>/<int:did_pay>', methods=[
    'GET',
    'POST',
])
@login.login_required
@user_is_admin
def finance(year, month, did_pay):
    """
    Renders finance page.
    did_pay = 0 - no filter
    did_pay = 1 - filter only paid
    did_pay = 2 - filter only unpaid
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
    users = User.query.all()
    orders = Order.query.filter(
        and_(
            Order.date >= month_begin,
            Order.date <= month_end,
        )
    ).all()
    finances = Finance.query.filter(
        and_(
            Finance.month == month,
            Finance.year == year,
        )
    ).all()
    finance_data = {}
    finance_user_list = []
    for user in users:
        finance_data[user.username] = {
            'username': user.username,
            'number_of_orders': 0,
            'month_cost': 0,
            'did_user_pay': False,
        }
        for order in orders:
            if user.username == order.user_name:
                finance_data[user.username]['number_of_orders'] += 1
                finance_data[user.username]['month_cost'] += order.cost
        for finance_query in finances:
            finance_user_list.append(finance_query.user_name)
            if finance_query.user_name == user.username \
                    and finance_query.did_user_pay:
                finance_data[user.username]['did_user_pay'] = True
        should_drop = (
            # user didn't bought anything
            finance_data[user.username]['month_cost'] == 0 or
            # show paid user and user did not pay
            (
                did_pay == 1 and
                not finance_data[user.username]['did_user_pay']
            ) or
            # show unpaid user and user paid
            (
                did_pay == 2 and
                (
                    finance_data[user.username]['did_user_pay']
                )
            )
        )
        if should_drop:
            del finance_data[user.username]

    pub_date = {'year': year, 'month': month_name[month]}

    finance_record = Finance()

    if request.method == 'POST':
        for row in finance_data.values():
            finance_record.did_user_pay = request.form.get(
                'did_user_pay_'+row['username'],
                'off',
            ) == 'on'
            finance_record.month = month
            finance_record.year = year
            finance_record.user_name = row['username']
            do_not_update = True
            for record in finances:
                if record.user_name == row['username']:
                    record.did_user_pay = finance_record.did_user_pay
                    do_not_update = False
            if do_not_update:
                db.session.add(finance_record)
        db.session.commit()
        flash('Finances changes submitted successfully')
        return redirect(url_for(
            'finance',
            year=year,
            month=month,
            did_pay=did_pay,
        ))
    p_year, p_month = previous_month(year, month)
    n_year, n_month = next_month(year, month)
    links = {
        'previous_month':
            url_for('finance', year=p_year, month=p_month, did_pay=did_pay),
        'next_month':
            url_for('finance', year=n_year, month=n_month, did_pay=did_pay),
    }
    return render_template(
        'finance.html',
        finance_data=finance_data,
        pub_date=pub_date,
        links=links,
    )


@app.route('/finance_mail_text', methods=['GET', 'POST'])
@login.login_required
@user_is_admin
def finance_mail_text():
    """
    Renders mail all page.
    """
    try:
        mail_data = MailText.query.first()
    except OperationalError:
        mail_data = None
    form = MailTextForm(formdata=request.form, obj=mail_data)

    if request.method == 'POST' and form.validate():
        if mail_data is None:
            texts = MailText()
            form.populate_obj(texts)
            db.session.add(texts)
        else:
            form.populate_obj(mail_data)
            db.session.commit()
        flash('Messages text updated')
        return redirect('finance_mail_text')

    return render_template(
        'finance_mail_text.html',
        form=form,
    )


@app.route('/finance_mail_all', methods=['GET', 'POST'])
@login.login_required
@user_is_admin
def finance_mail_all():
    """
    Renders mail all page.
    """
    this_month = datetime.date.today()
    month_begin = datetime.datetime(
        year=this_month.year,
        month=this_month.month,
        day=1,
        hour=0,
        minute=0,
        second=1
    )
    day = monthrange(this_month.year, this_month.month)[1]
    month_end = datetime.datetime(
        year=this_month.year,
        month=this_month.month,
        day=day,
        hour=23,
        minute=59,
        second=59
    )
    users = User.query.all()
    orders = Order.query.filter(
        and_(
            Order.date >= month_begin,
            Order.date <= month_end,
        )
    ).all()
    finances = Finance.query.filter(
        and_(
            Finance.month == this_month.month,
            Finance.year == this_month.year,
        )
    ).all()
    finance_user_list = []
    for finance_query in finances:
        finance_user_list.append(finance_query.user_name)
    finance_data = {}
    for user in users:
        finance_data[user.username] = {
            'username': user.username,
            'number_of_orders': 0,
            'month_cost': 0,
            'did_user_pay': False,
        }
        for order in orders:
            if user.username == order.user_name:
                finance_data[user.username]['number_of_orders'] += 1
                finance_data[user.username]['month_cost'] += order.cost
        if finance_data[user.username]['month_cost'] == 0 \
                or user.username not in finance_user_list:
            del finance_data[user.username]

    if request.method == 'POST':
        message_text = MailText.query.first()
        for record in finance_data.values():
            msg = Message(
                'Lunch {} / {} summary'.format(month_name[this_month.month],
                                               this_month.year),
                recipients=[record['username']],
            )
            msg.body = "In {} you ordered {} meals for {} PLN.\n {}".format(
                month_name[this_month.month],
                record['number_of_orders'],
                record['month_cost'],
                message_text.monthly_pay_summary,
                )
            mail.send(msg)
            flash('Mail send')
        return redirect('finance_mail_all')

    return render_template('finance_mail_all.html', finance_data=finance_data)


@app.route('/payment_remind/<string:username>/<int:slack>', methods=[
    'GET',
    'POST',
])
@login.login_required
@user_is_admin
def payment_remind(username, slack=0):
    """
    Sends mail to user with reminder or slack reminder.
    """
    this_month = datetime.date.today()
    message_text = MailText.query.first()
    msg = Message(
        'Lunch {} / {} payment reminder'.format(
            month_name[this_month.month],
            this_month.year
        ),
        recipients=[username],
    )
    if slack == 1:
        msg.body = message_text.pay_slacker_reminder
    else:
        msg.body = message_text.pay_reminder
    mail.send(msg)
    flash('Mail send')
    return redirect('finance')


@app.route('/finance_search', methods=['GET', 'POST'])
@login.login_required
@user_is_admin
def finance_search_view():
    """
    Renders company query page form.
    """
    form = FinanceSearchForm(request.form)
    if request.method == 'POST' and form.validate():
        return redirect(url_for(
            'finance',
            year=form.data['year'],
            month=form.data['month'],
            did_pay=form.data['did_pay']
        ))
    return render_template('finance_search.html', form=form)


@app.route('/random_meal/<int:courage>', methods=['GET', 'POST'])
@login.login_required
def random_food(courage):
    """
    Orders random meal.
    """
    day = datetime.date.today()
    today_from = datetime.datetime.combine(day, datetime.time(23, 59))
    today_to = datetime.datetime.combine(day, datetime.time(0, 0))
    foods = Order.query.filter(
        and_(
            Order.date <= today_from,
            Order.date >= today_to,
        )
    ).all()
    food_dict = Counter(foods)
    food_dict = food_dict.most_common()
    if len(food_dict) > 3:
        foods = [food_dict[0][0], food_dict[1][0], food_dict[2][0]]
    else:
        foods = Food.query.filter(
            and_(
                Food.date_available_from <= today_from,
                Food.date_available_to >= today_to,
                Food.o_type != 'menu',
            )
        ).all()
    food = choice(foods)
    if food.description.startswith('!RANDOM O'):
        food.description = food.description[15:]
    if courage >= 1:
        order = Order()
        if courage == 1:
            order.arrival_time = '12:00'
        elif courage == 2:
            order.arrival_time = '13:00'
        order.company = food.company
        order.cost = food.cost
        order.description = '!RANDOM ORDER!\n'
        order.description += food.description
        order.user_name = current_user.username
        db.session.add(order)
        db.session.commit()
        flash('! Random meal ordered !')
        return redirect('order')
    elif courage == 0:
        random_order = {
            "description": food.description,
            "cost": food.cost,
            "arrival_time": '12:00',
            "company": food.company
        }
        resp = jsonify(random_order)
        resp.status_code = 200
        return resp


@app.route('/send_daily_reminder', methods=['GET', 'POST'])
@login.login_required
def send_daily_reminder():
    """
    Sends daili reminder to all users.
    """
    day = datetime.date.today()
    today_beg = datetime.datetime.combine(day, datetime.time(00, 00))
    today_end = datetime.datetime.combine(day, datetime.time(23, 59))
    orders = Order.query.filter(
        and_(
            Order.date >= today_beg,
            Order.date <= today_end,
        )
    ).all()
    users = User.query.filter(User.i_want_daily_reminder).all()
    message_text = MailText.query.first()
    emails = ([])
    order_list = ([])
    for order in orders:
        order_list.append(order.user_name)
    for user in users:
        if user.username not in order_list:
            emails.append(user.username)
    msg = Message(
        '{} {}'.format(
            message_text.daily_reminder_subject,
            datetime.date.today()
        ),
        recipients=emails,
    )
    msg.body = message_text.daily_reminder
    mail.send(msg)
    return redirect('overview')


@app.route('/tv', methods=['GET', 'POST'])
@login.login_required
def orders_summary_for_tv():
    """
    View for TV showing all orders and reveling hard random orders.
    """
    day = datetime.date.today()
    today_beg = datetime.datetime.combine(day, datetime.time(00, 00))
    today_end = datetime.datetime.combine(day, datetime.time(23, 59))
    orders = Order.query.filter(
        and_(
            Order.date >= today_beg,
            Order.date <= today_end,
        )
    ).all()
    return render_template('tv.html', orders=orders)


@app.route('/finance_block_user', methods=['GET', 'POST'])
@login.login_required
def finance_block_user():
    """
    Allows to block specific user from ordering.
    """
    users = User.query.all()
    users_to_block = []
    users_to_unblock = []
    for user in users:
        if user.active:
            users_to_block.append((user.id, user.username))
        else:
            users_to_unblock.append((user.id, user.username))
    form_block = FinanceBlockUserForm(request.form)
    form_block.user_select.choices = users_to_block
    form_unblock = FinanceBlockUserForm(request.form)
    form_unblock.user_select.choices = users_to_unblock
    if request.method == 'POST' \
            and request.form['block_change'] == 'block':
        user = User.query.get(request.form['user_select'])
        user.active = False
        db.session.commit()
        flash('User blocked')
        return redirect('finance_block_user')
    elif request.method == 'POST' and \
            request.form['block_change'] == 'unblock':
        user = User.query.get(request.form['user_select'])
        user.active = True
        db.session.commit()
        flash('User unblocked')
        return redirect('finance_block_user')

    return render_template(
        'finance_block_user.html',
        form_block=form_block,
        form_unblock=form_unblock,
    )

@app.route('/finance_block_ordering', methods=['GET', 'POST'])
@login.login_required
def finance_block_ordering():
    """
    Allows to block ordering for everyone.
    """
    global ORDERING_IS_ACTIVE
    ORDERING_IS_ACTIVE = False
    flash('Now users can NOT order !')
    return redirect('day_summary')


@app.route('/finance_unblock_ordering', methods=['GET', 'POST'])
@login.login_required
def finance_unblock_ordering():
    """
    Allows to unblock ordering for everyone.
    """
    global ORDERING_IS_ACTIVE
    ORDERING_IS_ACTIVE = True
    flash('Now users can order :)')
    return redirect('day_summary')
