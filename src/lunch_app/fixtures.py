"""
Fixtures for database.
"""

from .main import db
from .models import Order, Food, User, Finance, MailText
from datetime import datetime, date, timedelta


def fill_db():
    """
    Fill the database for tests
    """
    user = User()
    user.email = 'e@e.pl'
    user.username = 'test_user'
    db.session.add(user)
    user_2 = User()
    user_2.email = 'd@d.pl'
    user_2.username = 'test@user.pl'
    user_2.i_want_daily_reminder = True
    db.session.add(user_2)
    user_3 = User()
    user_3.email = 'x@x.pl'
    user_3.username = 'x@x.pl'
    db.session.add(user_3)
    user_4 = User()
    user_4.email = 'reminder@user.pl'
    user_4.username = 'reminder@user.pl'
    user_4.i_want_daily_reminder = True
    db.session.add(user_4)
    order = Order()
    order.date = date(2015, 1, 5)
    order.description = 'Duzy Gruby Nalesnik'
    order.company = 'Tomas'
    order.cost = 123
    order.user_name = 'test_user'
    order.arrival_time = '12:00'
    db.session.add(order)
    order_2 = Order()
    order_2.description = 'Duzy Gruby Nalesnik'
    order_2.company = 'Pod Koziołkiem'
    order_2.cost = 244
    order_2.user_name = 'test_user'
    order_2.arrival_time = '12:00'
    db.session.add(order_2)
    order_3 = Order()
    order_3.description = 'Duzy Gruby Nalesnik'
    order_3.company = 'Pod Koziołkiem'
    order_3.cost = 244
    order_3.user_name = 'test@user.pl'
    order_3.arrival_time = '12:00'
    db.session.add(order_3)
    order_4 = Order()
    order_4.description = 'Maly Gruby Nalesnik'
    order_4.company = 'Pod Koziołkiem'
    order_4.cost = 1
    order_4.user_name = 'x@x.pl'
    order_4.arrival_time = '12:00'
    db.session.add(order_4)
    finance = Finance()
    finance.user_name = 'test_user'
    finance.month = 2
    finance.year = 2015
    finance.did_user_pay = True
    finance_2 = Finance()
    finance_2.user_name = 'test@user.pl'
    finance_2.month = 2
    finance_2.year = 2015
    finance_2.did_user_pay = False
    finance_3 = Finance()
    finance_3.user_name = 'reminder@user.pl'
    finance_3.month = 2
    finance_3.year = 2015
    finance_3.did_user_pay = False
    db.session.add(finance)
    db.session.add(finance_3)
    db.session.add(finance_2)
    meal_1 = Food()
    meal_1.company = "Tomas"
    meal_1.description = "Malza"
    meal_1.cost = 10
    meal_1.date_available_from = datetime.now() - timedelta(2)
    meal_1.date_available_to = datetime.now() + timedelta(2)
    meal_1.o_type = 'daniednia'
    meal_2 = Food()
    meal_2.company = "Pod Koziołkiem"
    meal_2.description = "Tiramisu"
    meal_2.cost = 20
    meal_2.date_available_from = datetime.now() - timedelta(5)
    meal_2.date_available_to = datetime.now() + timedelta(5)
    meal_2.o_type = 'tygodniowe'
    db.session.add(meal_1)
    db.session.add(meal_2)
    mailtxt = MailText()
    mailtxt.daily_reminder_subject = "STX Lunch daili_subject_reminder"
    mailtxt.daily_reminder = "daili1"
    mailtxt.monthly_pay_summary = "monthly2"
    mailtxt.pay_reminder = "reminder3"
    mailtxt.pay_slacker_reminder = 'slacker4'
    db.session.add(mailtxt)
    db.session.commit()
