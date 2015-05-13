# -*- coding: utf-8 -*-
# pylint: disable=invalid-name, no-member
"""
Defines views.
"""
from calendar import monthrange, month_name
from collections import Counter
import datetime
import logging
from random import choice

from flask import redirect, render_template, request, flash, url_for, jsonify
from flask.ext import login
from flask.ext.login import current_user
from flask.ext.mail import Message
from sqlalchemy import and_, or_, desc
from sqlalchemy.orm import load_only

from .main import app, db, mail
from .forms import (
    OrderForm, AddFood, OrderEditForm,
    UserOrders, CompanyOrders, MailTextForm,
    UserPreferences, FinanceSearchForm, CompanyAddForm,
    FoodRateForm, FinanceBlockUserForm, PizzaChooseForm,
    CreateConflict, ResolveConflict,
)
from .models import (
    Order, Food, User,
    Finance, MailText, Company,
    Pizza, Conflict,
)
from .permissions import user_is_admin
from .utils import (
    next_month, previous_month, send_daily_reminder,
    add_daily_koziolek, get_week_from_tomas, ordering_is_active,
    server_url, current_day_orders, current_day_meals,
    current_day_meals_and_companies, month_orders, add_a_new_meal,
    change_ordering_status,
)

log = logging.getLogger(__name__)


@app.route('/')
@app.route('/<error>')
def index(error=None):
    """
    Gplus login page.
    """
    if not current_user.is_anonymous() and \
            '@stxnext.pl' in current_user.username:
        return redirect('order')
    elif not current_user.is_anonymous() or error:
        msg = "Sadly you are not a hero, but you can try and join us."
        return render_template('index.html', msg=msg)
    return render_template('index.html')


@app.route('/overview', methods=['GET', 'POST'])
@login.login_required
def overview():
    """
    Overview page.
    """
    user = User.query.get(current_user.id)
    form = UserPreferences(formdata=request.form, obj=user)
    if request.method == 'POST' and form.validate():
        user.i_want_daily_reminder = \
            request.form.get('i_want_daily_reminder') == 'y'
        user.preferred_arrival_time = request.form.get(
            'preferred_arrival_time'
        )
        db.session.commit()
        flash('User preferences updated')
        return redirect('overview')
    return render_template('overview.html', form=form, user=user)


@app.route('/order', methods=['GET', 'POST'])
@login.login_required
def create_order():
    """
    Create new order page.
    """
    if not current_user.is_active():
        flash(MailText.query.get(1).blocked_user_text)
        return redirect('overview')
    if not ordering_is_active():
        flash(MailText.query.get(1).ordering_is_blocked_text)
        return redirect('overview')
    form = OrderForm(request.form)
    companies = Company.query.all()
    form.company.choices = [
        (comp.name, "Order from {}".format(comp.name)) for comp in companies
    ]
    if current_user.preferred_arrival_time:
        form.arrival_time.data = current_user.preferred_arrival_time
    foods, companies_current, companies_menu = \
        current_day_meals_and_companies(companies)
    if request.method == 'POST' and form.validate():
        order = Order()
        form.populate_obj(order)
        order.arrival_time = request.form['arrival_time']
        order.user_name = current_user.username
        order.description = order.description.strip()
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
    return render_template(
        'order.html',
        form=form,
        foods=foods,
        companies_current=companies_current,
        companies_menu=companies_menu,
        random_ordering_is_allowed=False,
    )


@app.route('/add_food', methods=['GET', 'POST'])
@login.login_required
@user_is_admin
def add_food():
    """
    Add new food page.
    """
    form = AddFood(request.form)
    companies = Company.query.all()
    form.company.choices = [(comp.name, comp.name) for comp in companies]
    if request.method == 'POST' and form.validate() \
            and request.form['add_meal'] == 'add':
        food = Food()
        form.populate_obj(food)
        db.session.add(food)
        db.session.commit()
        flash('Food added')
        return redirect('add_food')
    elif request.method == 'POST' and form.validate() \
            and request.form['add_meal'] == 'bulk':
        foods = form.description.data
        foods = foods.replace('\r', '').split('\n')
        number_of_foods_aded = 0
        for food in foods:
            if food.strip():
                add_a_new_meal(
                    form.cost.data,
                    food,
                    form.date_available_from.data,
                    form.date_available_to.data,
                    form.company.data,
                    type=form.o_type.data
                )
                number_of_foods_aded += 1
        db.session.commit()
        flash('{} foods added'.format(number_of_foods_aded))
        return redirect('add_food')
    companies = Company.query.all()
    foods, companies_current, companies_menu = \
        current_day_meals_and_companies(companies)
    return render_template(
        'add_food.html',
        form=form,
        foods=foods,
        companies_current=companies_current,
        companies_menu=companies_menu,
    )


@app.route('/day_summary', methods=['GET', 'POST'])
@login.login_required
@user_is_admin
def day_summary():
    """
    Day orders summary.
    """
    companies = Company.query.all()
    orders = current_day_orders()
    order_details = {}
    orders_summary = {
        '12:00': {},
        '13:00': {},
    }
    for comp in companies:
        order_details[comp.name] = {
            '12:00': set([]),
            'cost12': 0,
            '13:00': set([]),
            'cost13': 0,
        }
        orders_summary['12:00'][comp.name] = {}
        orders_summary['13:00'][comp.name] = {}
        for order in orders:
            foods = order.description
            foods = foods.replace('\r', '').split('\n')
            for food in foods:
                food = food.strip()
                if food != "!RANDOM ORDER!" and order.company == comp.name:
                    if order.arrival_time == '12:00':
                        if order not in order_details[comp.name]['12:00']:
                            order_details[comp.name]['cost12'] += order.cost
                        order_details[comp.name]['12:00'].add(order)
                        try:
                            orders_summary['12:00'][comp.name][food] += 1
                        except KeyError:
                            orders_summary['12:00'][comp.name][food] = 1
                    elif order.arrival_time == '13:00':
                        if order not in order_details[comp.name]['12:00']:
                            order_details[comp.name]['cost13'] += order.cost
                        order_details[comp.name]['13:00'].add(order)
                        try:
                            orders_summary['13:00'][comp.name][food] += 1
                        except KeyError:
                            orders_summary['13:00'][comp.name][food] = 1

    return render_template(
        'day_summary.html',
        order_details=order_details,
        companies=companies,
        orders_summary=orders_summary,
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
    temp = "{}".format(MailText.query.get(1).info_page_text)
    info = temp.split('\n')
    if len(info) < 2:
        info = "None"
    return render_template('info.html', info=info)


@app.route('/order_details/<int:order_id>', methods=['GET', 'POST'])
@login.login_required
def order_details(order_id):
    """
    Renders orders detail page.
    """
    order = Order.query.get(order_id)
    return render_template('order_details.html', order=order)


@app.route('/order_edit/<int:order_id>/', methods=['GET', 'POST'])
@login.login_required
@user_is_admin
def edit_order(order_id):
    """
    Renders order edit page.
    """
    companies = Company.query.all()
    order = Order.query.get(order_id)
    users_db = User.query.all()
    users = [user.username for user in users_db]
    form = OrderEditForm(formdata=request.form, obj=order)
    form.company.choices = [(comp.name, comp.name) for comp in companies]
    if request.method == 'POST' and form.validate():
        form.populate_obj(order)
        if form.user_name.data not in users:
            new_user = User()
            new_user.username = form.user_name.data
            new_user.email = form.user_name.data
            db.session.add(new_user)
        db.session.commit()
        flash('Order edited')
        return redirect('day_summary')
    return render_template(
        'order_edit.html',
        form=form,
        order=order,
        users=users,
    )


@app.route('/delete_order/<int:order_id>', methods=['GET', 'POST'])
@login.login_required
@user_is_admin
def delete_order(order_id):
    """
    Deletes order.
    """
    order = Order.query.get(order_id)
    db.session.delete(order)
    db.session.commit()
    return redirect('day_summary')


@app.route('/order_list', methods=['GET', 'POST'])
@login.login_required
def order_list():
    """
    Renders order list page form.
    """
    form = UserOrders(request.form)
    form.user.choices = [(user.id, user.username) for user in User.query.all()]
    if not current_user.is_admin():
        form.user.data = current_user.id
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
    user = User.query.get(user_id)
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
    pub_date = {'year': year, 'month': month_name[month]}
    user = User.query.get(user_id)
    orders = month_orders(year, month, user=user.username)
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
    companies = Company.query.all()
    pub_date = {'year': year, 'month': month_name[month]}
    orders = month_orders(year, month)
    orders_data = {}
    for comp in companies:
        orders_data[comp.name] = 0
        for order in orders:
            if order.company == comp.name:
                orders_data[comp.name] += order.cost
    return render_template(
        'company_summary_month_view.html',
        orders_data=orders_data,
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
    users = User.query.all()
    orders = month_orders(year, month)
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
            'email': user.email,
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
    if request.method == 'POST':
        for row in finance_data.values():
            finance_record = Finance()
            finance_record.did_user_pay = (request.form.get(
                'did_user_pay_' + row['username'],
            ) == 'on')
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
    Renders mail and info text edit page.
    """
    mail_data = MailText.query.first()
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
    Renders mail to all page.
    """
    year, month = previous_month(
        datetime.date.today().year,
        datetime.date.today().month,
    )
    orders = month_orders(year, month)
    finances = Finance.query.filter(
        and_(
            Finance.month == month,
            Finance.year == year,
        )
    ).all()
    finance_data = {}
    finance_user_list = []
    users = User.query.all()
    for user in users:
        finance_data[user.username] = {
            'username': user.username,
            'email': user.email,
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
            finance_data[user.username]['month_cost'] == 0
        )

        if should_drop:
            del finance_data[user.username]
    message_text = MailText.query.first()
    if request.method == 'POST' and request.form['send_mail'] == 'all':
        for record in finance_data.values():
            msg = Message(
                'Lunch {} / {} summary'.format(month_name[month],
                                               year),
                recipients=[record['email']],
            )
            msg.body = "In {} you ordered {} meals for {} PLN.\n {}".format(
                month_name[month],
                record['number_of_orders'],
                record['month_cost'],
                message_text.monthly_pay_summary,
            )
            mail.send(msg)
        flash('Mail send')
        return redirect('finance_mail_all')
    if request.method == 'POST' and request.form['send_mail'] == 'remind_all':
        for record in finance_data.values():
            if not record['did_user_pay']:
                msg = Message(
                    'Lunch app payment reminder',
                    recipients=[record['email']],
                )
                msg.body = "In {} you ordered {} meals for {} PLN.\n{}".format(
                    month_name[month],
                    record['number_of_orders'],
                    record['month_cost'],
                    message_text.pay_reminder,
                )
                mail.send(msg)
                flash('Mail send')
        return redirect('finance_mail_all')

    return render_template('finance_mail_all.html', finance_data=finance_data)


@app.route('/payment_remind/<string:email>/<int:slack>', methods=[
    'GET',
    'POST',
])
@login.login_required
@user_is_admin
def payment_remind(email, slack=0):
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
        recipients=[email],
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
    if not ordering_is_active():
        flash(MailText.query.get(1).ordering_is_blocked_text)
        return redirect('overview')
    foods = current_day_orders()
    food_dict = Counter([order.description for order in foods]).most_common()
    if len(food_dict) >= 3:
        foods = [food_dict[0][0], food_dict[1][0], food_dict[2][0]]
        food = choice(foods)
        food = Order.query.filter(Order.description == food).first()
    else:
        foods = current_day_meals()
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
@user_is_admin
def send_daily_reminder_view():
    """
    Sends daily reminder to all users view.
    """
    send_daily_reminder()
    return redirect('overview')


@app.route('/finance_companies', methods=['GET', 'POST'])
@login.login_required
@user_is_admin
def finance_companies_view():
    """
    Add new company page.
    """
    form = CompanyAddForm(request.form)
    if request.method == 'POST' and form.validate():
        company = Company()
        form.populate_obj(company)
        db.session.add(company)
        db.session.commit()
        flash('Company added')
        return redirect('finance_companies')
    companies = Company.query.all()
    return render_template(
        'finance_companies.html',
        form=form,
        companies=companies
    )


@app.route('/food_rate', methods=['GET', 'POST'])
@login.login_required
def food_rate():
    """
    Create new order page.
    """
    form = FoodRateForm(request.form)
    day = datetime.date.today()
    today_beg = datetime.datetime.combine(day, datetime.time(00, 00, 00))
    today_end = datetime.datetime.combine(day, datetime.time(23, 59, 59))
    order = Order.query.filter(
        and_(
            Order.date >= today_beg,
            Order.date <= today_end,
            Order.user_name == current_user.username,
        )
    ).first()
    if not order:
        flash("You didn't order anything today so you cannot rate the food")
        return redirect('overview')
    if current_user.rate_timestamp == datetime.date.today():
        flash("You already rated today come back tomorow :-)")
        return redirect('overview')
    foods = current_day_meals()
    food_list = []
    order.description = order.description.strip()
    for food in foods:
        food.description = food.description.strip()
        if food.description == order.description:
            form.food.choices = [(food.id, food.description)]
            break
        else:
            if food.description.strip():
                food_list.append((food.id, food.description))
                form.food.choices = food_list
    if request.method == 'POST' and form.validate():
        food = Food.query.get(form.food.data)
        if food.rating:
            food.rating = (food.rating + form.rate.data) / 2
        else:
            food.rating = form.rate.data
        user = User.query.get(current_user.id)
        user.rate_timestamp = datetime.date.today()
        db.session.commit()
        flash("You rated the food successfully")
        return redirect('overview')
    return render_template('food_rate.html', form=form)


@app.route('/finance_block_user', methods=['GET', 'POST'])
@login.login_required
@user_is_admin
def finance_block_user():
    """
    Allows to block specific user from ordering.
    """
    users = User.query.all()
    users_to_block = [
        (user.id, user.username)
        for user in users if user.active
    ]
    users_to_unblock = [
        (user.id, user.username)
        for user in users if not user.active
    ]
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
@user_is_admin
def finance_block_ordering():
    """
    Allows to block ordering for everyone.
    """
    change_ordering_status(False)
    flash('Now users can NOT order !')
    return redirect('day_summary')


@app.route('/finance_unblock_ordering', methods=['GET', 'POST'])
@login.login_required
@user_is_admin
def finance_unblock_ordering():
    """
    Allows to unblock ordering for everyone.
    """
    change_ordering_status(True)
    flash('Now users can order :)')
    return redirect('day_summary')


@app.route('/add_daily_koziolek', methods=['GET', 'POST'])
@login.login_required
@user_is_admin
def add_daily_koziolek_view():
    """
    Adds meal of a day from pod koziolek
    """
    add_daily_koziolek()
    flash('Meals of a day from Pod Koziolek have been added')
    return redirect('add_food')


@app.route('/add_week_tomas', methods=['GET', 'POST'])
@login.login_required
@user_is_admin
def get_week_from_tomas_view():
    """
    Adds weak meals from Tomas ! use only on mondays ! - view
    """
    get_week_from_tomas()
    flash('Weak of meals from Tomas have been added.')
    return redirect('add_food')


@app.route('/order_pizza_for_everybody', methods=['GET', 'POST'])
@login.login_required
def order_pizza_for_everybody():
    """
    Orders pizza for every user and sedns him an e-mail.
    """
    new_event = Pizza()
    new_event.who_created = current_user.username
    new_event.pizza_ordering_is_allowed = True
    new_event.users_already_ordered = ""
    db.session.add(new_event)
    db.session.commit()
    new_event = Pizza.query.all()[-1]
    new_event_id = new_event.id
    event_url = server_url() + url_for(
        "pizza_time_view",
        happening=new_event_id,
    )
    stop_url = server_url() + url_for(
        "pizza_time_stop",
        happening=new_event_id,
    )
    users = User.query.filter(User.active).all()
    emails = [user.email for user in users]
    text = 'You succesfully orderd pizza for all You can check who wants' \
           ' what here:\n{}\n to finish the pizza orgy click here\n{}\n ' \
           'than order pizza!'.format(event_url, stop_url)
    msg = Message(
        'Lunch app PIZZA TIME',
        recipients=emails,
    )
    msg.body = '{} ordered pizza for everyone ! \n order it here:\n\n' \
               '{}\n\n and thank him!'.format(current_user.username, event_url)
    mail.send(msg)
    msg = Message(
        'Lunch app PIZZA TIME',
        recipients=[current_user.username],
    )
    msg.body = text
    mail.send(msg)
    flash(text)
    return redirect(url_for("pizza_time_view", happening=new_event_id))


@app.route('/tv', methods=['GET', 'POST'])
@login.login_required
def orders_summary_for_tv():
    """
    View for TV showing all orders and reveling hard random orders.
    """
    orders = current_day_orders()
    return render_template('tv.html', orders=orders)


@app.route('/pizza_time/<int:happening>', methods=['GET', 'POST'])
@login.login_required
def pizza_time_view(happening):
    """
    Shows pizza menu, order Form and orders summary.
    """
    pizzas_db = Pizza.query.get(happening)
    form = PizzaChooseForm(request.form)
    if request.method == 'POST' and form.validate():
        if not pizzas_db.pizza_ordering_is_allowed:
            flash('Pizza time finished !')
            return redirect(url_for('pizza_time_view', happening=happening))
        if current_user.username in pizzas_db.users_already_ordered:
            flash('You already ordered !')
            return redirect(url_for('pizza_time_view', happening=happening))
        pizza = form.description.data
        pizza = pizza.strip()
        size = form.pizza_size.data
        try:
            try:
                pizzas_db.ordered_pizzas[pizza][size] \
                    += current_user.username
            except KeyError:
                try:
                    pizzas_db.ordered_pizzas[pizza] += {
                        size: current_user.username
                    }
                except KeyError:
                    pizzas_db.ordered_pizzas[pizza] = {
                        size: current_user.username
                    }
        except TypeError:
            pizzas_db.ordered_pizzas = {
                form.description.data: {
                    form.pizza_size.data: current_user.username,
                }
            }
        pizzas_db.users_already_ordered += current_user.username + " "
        db.session.commit()
        flash('You successfully ordered a pizza ;-)')
        return redirect(url_for('pizza_time_view', happening=happening))
    pizzas_ordered = pizzas_db.ordered_pizzas
    pizzas_active = pizzas_db.pizza_ordering_is_allowed
    return render_template(
        'pizza_time.html',
        form=form,
        pizzas_ordered=pizzas_ordered,
        pizzas_active=pizzas_active,
    )


@app.route('/pizza_time_stop/<int:happening>', methods=['GET', 'POST'])
@login.login_required
def pizza_time_stop(happening):
    """
    Stops pizza time.
    """
    pizzas_db = Pizza.query.get(happening)
    if current_user.username != pizzas_db.who_created:
        flash('! Only event creator can stop the event !')
        return redirect(url_for('pizza_time_view', happening=happening))
    pizzas_db.pizza_ordering_is_allowed = False
    db.session.commit()
    return redirect(url_for('pizza_time_view', happening=happening))


@app.route('/food_edit/<int:food_id>', methods=['GET', 'POST'])
@login.login_required
@user_is_admin
def food_edit_view(food_id):
    """
    Renders food edit page.
    """
    companies = Company.query.all()
    food = Food.query.get(food_id)
    form = AddFood(formdata=request.form, obj=food)
    form.company.choices = [(comp.name, comp.name) for comp in companies]
    if request.method == 'POST' and form.validate():
        form.populate_obj(food)
        db.session.commit()
        flash('Food edited')
        return redirect('add_food')
    return render_template(
        'food_edit.html',
        form=form,
        food=food,
    )


@app.route('/food_delete/<int:food_id>', methods=['GET', 'POST'])
@login.login_required
@user_is_admin
def delete_food(food_id):
    """
    Deletes food.
    """
    db.session.delete(Food.query.get(food_id))
    db.session.commit()
    return redirect('add_food')


@app.route('/conflicts', methods=['GET', 'POST'])
@login.login_required
def conflicts():
    """
    Renders conflict view page.
    """
    if current_user.is_admin():
        conflicts = Conflict.query.all()
    else:
        conflicts = Conflict.query.filter(
            or_(
                Conflict.created_by_user == current_user.username,
                Conflict.user_connected == current_user.username,
            )
        ).all()

    return render_template("conflicts.html", conflicts=conflicts)


@app.route('/conflict_create/<int:order_id>', methods=['GET', 'POST'])
@login.login_required
def conflict_create(order_id):
    """
    Renders conflict create page.
    """
    order = Order.query.get(order_id)
    form = CreateConflict(formdata=request.form)
    form.user_connected.choices = [
        (user.username, user.username) for user in User.query.options(
            load_only("username")
        ).all()
    ]
    form.user_connected.choices.append(("None", "None"))
    form.user_connected.default = ("None", "None")
    if request.method == 'POST':
        conflict = Conflict()
        conflict.did_order_come = request.form.get("did_order_come") == 'y'
        conflict.i_know_who = request.form.get("i_know_who") == 'y'
        conflict.user_connected = request.form.get("user_connected")
        conflict.order_connected = order.id
        conflict.created_by_user = current_user.username
        db.session.add(conflict)
        db.session.commit()
        if conflict.i_know_who:
            new_conflict = Conflict.query.order_by(Conflict.date_added.desc()).first()
            conflict_url = server_url() + url_for(
                "conflict_resolve",
                conf_id=new_conflict.id,
            )
            msg = Message(
                'Lunch app new conflict',
                recipients=[conflict.user_connected],
            )
            msg.body = 'You were chosen as the one who ate my lunch! ' \
                       'Please use the link below to respond' \
                       ' \n\n {}'.format(conflict_url)
            mail.send(msg)
        flash('Conflict created')
        return redirect('my_orders')
    return render_template("conflict_create.html", form=form)


@app.route('/conflict_resolve/<int:conf_id>', methods=['GET', 'POST'])
@login.login_required
def conflict_resolve(conf_id):
    """
    Renders conflict resolve page.
    """
    conflict = Conflict.query.get(conf_id)
    form = ResolveConflict(formdata=request.form, obj=conflict)
    if current_user.is_admin():
        form.resolved_by.choices = [
            ("Not resolved yet", "Not resolved yet"),
            ("Order did not come", "Order did not come"),
            ("Order come but someone ate it", "Order come but someone ate it"),
        ]
        info = ["Order did not come -- means that the order cost will be "
                "changed to 0 and there will be additional description in "
                "the order",
                "Order come but someone ate it -- does not change anything.",
                "Not resolved yet -- does not change anything"]
    elif current_user.username == conflict.user_connected:
        form.resolved_by.choices = [
            ("I did not eat your lunch", "I did not eat your lunch"),
            ("I'm sorry, I ate your meal", "I'm sorry, I ate your meal"),
        ]
        info = ["I'm sorry, I ate your meal -- means that the order will be "
                "asinged to you.",
                "I did not eat your lunch -- does not change anything"]
    else:
        flash("You cannot resolve conflicts by yourself")
        return redirect('conflicts')

    if request.method == 'POST' and form.validate():
        conflict.resolved = (request.form.get("resolved") == "y")
        conflict.resolved_by = request.form["resolved_by"]
        conflict.notes = request.form.get("notes")
        msg = Message(
            'Lunch app conflict update',
            recipients=[conflict.created_by_user],
        )
        if conflict.resolved_by == "Order did not come":
            order = Order.query.get(conflict.order_connected)
            order.cost = 0
            order.description = "ORDER DID NOT COME\n" + order.description
            msg.body = "The order \n{}\n did not come so it cost was changed" \
                       "to 0 pln and it got properly described on your list " \
                       "of orders.".format(order.description)
        elif conflict.resolved_by == "I'm sorry, I ate your meal":
            conflict.resolved = True
            order = Order.query.get(conflict.order_connected)
            order.user_name = current_user.username
            msg.body = "{} is sorry he ate Your meal the order is now" \
                       "assigned to him/her".format(conflict.user_connected)
        else:
            url = server_url() + url_for("conflict_resolve", conf_id=conf_id)
            msg.body = "Your conflict was updated check out the changes " \
                       "here: \n {}".format(url)
        mail.send(msg)
        db.session.commit()
        flash('Conflict updated')
        return redirect('conflicts')
    return render_template("conflict_resolve.html", form=form, info=info)
