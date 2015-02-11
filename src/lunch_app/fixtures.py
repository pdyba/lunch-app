"""
Fixtures for database.
"""
from datetime import datetime, date, timedelta
from unittest.mock import Mock
from os import path

from .main import db
from .models import Order, Food, User, Finance, MailText, OrderingInfo


def allow_ordering():
    """
    Creates the most necessary records in data base.
    """
    ordering_info = OrderingInfo()
    ordering_info.is_allowed = True
    db.session.add(ordering_info)
    mailtxt = MailText()
    mailtxt.daily_reminder_subject = "STX Lunch daili_subject_reminder"
    mailtxt.daily_reminder = "daili1"
    mailtxt.monthly_pay_summary = "monthly2"
    mailtxt.pay_reminder = "reminder3"
    mailtxt.pay_slacker_reminder = 'slacker4'
    mailtxt.blocked_user_text = 'YouareBlocked'
    mailtxt.ordering_is_blocked_text = 'OrderingIsBlocked'
    db.session.add(mailtxt)
    db.session.commit()


def fill_db():
    """
    Fill the database for tests
    """
    allow_ordering()
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
    db.session.commit()


MOCK_ADMIN = Mock()
MOCK_ADMIN.is_admin.return_value = True
MOCK_ADMIN.username = 'test_user'
MOCK_ADMIN.active = True
MOCK_ADMIN.is_anonymous.return_value = False
MOCK_ADMIN.is_active.return_value = True
MOCK_ADMIN.email = 'mock@mock.com'

MOCK_DATA_KOZIOLEK = Mock()
MOCK_DATA_KOZIOLEK.return_value = {
    'danie_dania_1':
        '1.Kotlet schabowy z ziemniakami gotowanymi i kapusta zasmażana',
    'danie_dania_2':
        '2.Placki ziemniaczane z gulaszem wieprzowym i surówka',
    'zupa_dnia':
        'Zupa Ogórkowa'
}
MOCK_DATA_TOMAS = Mock()
MOCK_DATA_TOMAS.return_value = {
    'dzien_2': {
        'dania': [
            'Pierś z kurczaka panierowana faszerowana boczkiem i serem.',
            'Pulpety wieprzowe w sosie koperkowym, ryż, marchew z groszkiem.',
            'Sałatka z kurczakiem, warzywami i sosem czosnkowym.',
        ],
        'zupy': [
            'żurek',
            'grochówka',
        ],
        'zupa_i_dania': [
            'żurek + Pierś z kurczaka panierowana faszerowana boczkiem.',
            'żurek + Pulpety wieprzowe w sosie koperkowym, ryż, marchew.',
            'żurek + Sałatka z kurczakiem, warzywami i sosem czosnkowym.',
            'grochówka + Pierś z kurczaka panierowana faszerowana boczkiem.',
            'grochówka + Pulpety wieprzowe w sosie koperkowym, ryż.',
            'grochówka + Sałatka z kurczakiem, warzywami i sosem czosnkowym.',
        ]
    },
    'diet': [
        'ok.440kcal Polędwiczki drobiowe 120g, ryż 200g, bukiet warzyw 150g.',
        'ok.490kcal Pierś drobiowa z grilla 120g, kasza  200g, sałata  150g.',
    ],
    'dzien_4': {
        'dania': [
            'Medalion drobiowy panierowany zapiekany z ananasem, ziemniaki.',
            'Leczo węgierskie z mięsem wieprzowym, ryż, surówka kapusty.',
            'Sałatka grillowanym mięsem, warzywami i sosem czosnkowym.',
        ],
        'zupy': [
            'żurek',
            'krem z brokuł',
        ],
        'zupa_i_dania': [
            'żurek + Medalion drobiowy panierowany zapiekany z ananasem.',
            'żurek + Leczo węgierskie z mięsem wieprzowym, ryż, surówka.',
            'żurek + Sałatka grillowanym mięsem, warzywami i sosem czosnko.',
            'krem z brokuł + Medalion drobiowy panierowany zapiekany.',
            'krem z brokuł + Leczo węgierskie z mięsem wieprzowym, ryż.',
            'krem z brokuł + Sałatka grillowanym mięsem, warzywami.',
        ]
    },
    'dzien_1': {
        'dania': [
            'Kawałki kurczaka w sosie chińskim z warzywami, ryż, sałata.',
            'Schab panierowany zapiekany z pieczarkami, ziemniaki.',
            'Sałatka z serem feta, warzywami i sosem vinegret.',
        ],
        'zupy': [
            'żurek',
            'kapuśniak',
        ],
        'zupa_i_dania': [
            'żurek + Kawałki kurczaka w sosie chińskim z warzywami.',
            'żurek + Schab panierowany zapiekany z pieczarkami.',
            'żurek + Sałatka z serem feta, warzywami i sosem vinegret.',
            'kapuśniak + Kawałki kurczaka w sosie chińskim z warzywami.',
            'kapuśniak + Schab panierowany zapiekany z pieczarkami.',
            'kapuśniak + Sałatka z serem feta, warzywami i sosem vinegret.',
        ]
    },
    'dzien_5': {
        'dania': [
            'Miruna panierowana, ziemniaki, surówka z kiszonej kapusty.',
            'Naleśniki zapiekane z kurczakiem (3 szt.), sałata.',
            'Sałatka z tuńczykiem, warzywami, jajkiem i sosem vinegret.',
        ],
        'zupy': [
            'żurek',
            'barszcz ukraiński',
        ],
        'zupa_i_dania': [
            'żurek + Miruna panierowana, ziemniaki, surówka.',
            'żurek + Naleśniki zapiekane z kurczakiem (3 szt.).',
            'żurek + Sałatka z tuńczykiem, warzywami, jajkiem.',
            'barszcz ukraiński + Miruna panierowana, ziemniaki.',
            'barszcz ukraiński + Naleśniki zapiekane z kurczakiem (3 szt.).',
            'barszcz ukraiński + Sałatka z tuńczykiem, warzywami.',
        ]
    },
    'dzien_3': {
        'dania': [
            'Filet drobiowy w płatkach kukurydzianych, ziemniaki, surówka.',
            'Karkówka z grilla, frytki, sałata z warzywami.',
            'Sałatka z warzywami, serem mozzarella i sosem winegret.',
        ],
        'zupy': [
            'żurek',
            'ogórkowa',
        ],
        'zupa_i_dania': [
            'żurek + Filet drobiowy w płatkach kukurydzianych.',
            'żurek + Karkówka z grilla, frytki, sałata.',
            'żurek + Sałatka z warzywami, serem mozzarella.',
            'ogórkowa + Filet drobiowy w płatkach kukurydzianych.',
            'ogórkowa + Karkówka z grilla, frytki, sałata z warzywami.',
            'ogórkowa + Sałatka z warzywami, serem mozzarella.',
        ]
    }
}

MOCK_WWW_TOMAS = Mock()
MOCK_WWW_TOMAS.return_value = open(
    path.abspath(
        path.join(path.dirname(__file__), '../../etc/mock_tomas.html')
    )
)

MOCK_WWW_KOZIOLEK = Mock()
MOCK_WWW_KOZIOLEK.return_value = open(
    path.abspath(
        path.join(path.dirname(__file__), '../../etc/mock_koziolek.html')
    )
)
