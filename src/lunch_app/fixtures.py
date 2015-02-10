"""
Fixtures for database.
"""

from .main import db
from .models import Order, Food, User, Finance, MailText, Company
from datetime import datetime, date, timedelta


def fill_company():
    """
    Fill companies database for tests
    """
    company_1 = Company()
    company_1.name = 'Tomas'
    company_1.web_page = 'www.tomas.pl'
    company_1.address = 'ul dluga 5 99-343 poznan'
    company_1.telephone = '1234567890'
    db.session.add(company_1)
    company_2 = Company()
    company_2.name = 'Pod Koziołkiem'
    company_2.web_page = 'www.pod-koziolkiem.pl'
    company_2.address = 'ul ciekawa 5 66-554 Pozan'
    company_2.telephone = '0987654321'
    db.session.add(company_2)
    db.session.commit()


def fill_user():
    """
    Fill user database for tests
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
    db.session.commit()


def fill_order():
    """
    Fill the database for tests
    """
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
    db.session.commit()


def fill_food():
    """
    Fill food database for tests
    """
    meal_1 = Food()
    meal_1.company = "Tomas"
    meal_1.description = "Malza"
    meal_1.cost = 10
    meal_1.date_available_from = datetime.now() - timedelta(2)
    meal_1.date_available_to = datetime.now() + timedelta(2)
    meal_1.o_type = 'daniednia'
    db.session.add(meal_1)
    meal_2 = Food()
    meal_2.company = "Pod Koziołkiem"
    meal_2.description = "Tiramisu"
    meal_2.cost = 20
    meal_2.date_available_from = datetime.now() - timedelta(5)
    meal_2.date_available_to = datetime.now() + timedelta(5)
    meal_2.o_type = 'tygodniowe'
    db.session.add(meal_2)
    db.session.commit()


def fill_finance():
    """
    Fill food database for tests
    """
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
    db.session.commit()

def fill_db():
    """
    Fill the database for tests
    """
    fill_company()
    fill_user()
    fill_order()
    fill_food()
    fill_finance()
    mailtxt = MailText()
    mailtxt.daily_reminder_subject = "STX Lunch daili_subject_reminder"
    mailtxt.daily_reminder = "daili1"
    mailtxt.monthly_pay_summary = "monthly2"
    mailtxt.pay_reminder = "reminder3"
    mailtxt.pay_slacker_reminder = 'slacker4'
    db.session.add(mailtxt)
    db.session.commit()
