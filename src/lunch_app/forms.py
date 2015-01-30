# -*- coding: utf-8 -*-
"""
Lunch App Forms
"""
# pylint: disable=too-few-public-methods

from wtforms import (
    Form,
    validators,
    TextAreaField,
    IntegerField,
    BooleanField,
    SelectField,
    DateField,
)

from datetime import datetime, date


class OrderForm(Form):
    """
    New Order Creation Form
    """

    description = TextAreaField(
        "description",
        validators=[validators.DataRequired('Please enter your order.')],
    )
    cost = IntegerField(
        'cost',
        validators=[
            validators.DataRequired('Please enter cost.'),
            validators.NumberRange(
                min=0,
                max=999,
                message='Cost has to be a positive value',
                ),
        ]
    )
    arrival_time = SelectField(
        'arrival_time',
        validators=[validators.DataRequired("Please choose delivery time.")],
        choices=[
            ('12:00', 'Order on 12:00'),
            ('13:00', 'Order on 13:00'),
        ]
    )
    company = SelectField(
        'company',
        validators=[validators.DataRequired("Please choose company.")],
        choices=[
            ('Pod Koziołkiem', 'Order from Pod Koziołkiem'),
            ('Tomas', 'Order from Tomas'),
        ]
    )
    send_me_a_copy = BooleanField('send_me_a_copy', default=False)


class OrderEditForm(OrderForm):
    """
    New Order Eidt Form
    """
    user_name = TextAreaField("description")
    date = DateField("date")


class UserOrders(Form):
    """
    New User query Form
    """
    year = IntegerField(
        'year',
        validators=[validators.DataRequired('Please enter your Year.')]
    )
    month = IntegerField('month', validators=[validators.Optional()])
    user = SelectField('user_id', coerce=int)


class CompanyOrders(Form):
    """
    New User query Form
    """
    year = IntegerField(
        'year',
        validators=[validators.DataRequired('Please enter your Year.')]
    )
    month = IntegerField(
        'month',
        validators=[validators.DataRequired('Please enter your Month.')]
    )


class AddFood(Form):
    """
    New Order Creation Form
    """
    company = SelectField(
        'company',
        validators=[validators.DataRequired("Please choose company.")],
        choices=[
            ('Pod Koziołkiem', 'Pod Koziołkiem'),
            ('Tomas', 'Tomas'),
        ]
    )
    description = TextAreaField(
        "description",
        validators=[validators.DataRequired("Please enter order description.")]
    )
    cost = IntegerField(
        'cost',
        validators=[
            validators.DataRequired('Please enter cost.'),
            validators.NumberRange(
                min=0,
                max=999,
                message='Cost has to be provided and be a positive value',
                ),
        ]
    )
    date_available_from = DateField(
        label='date_available',
        default=datetime(2015, 1, 1, 0, 0, 0),
        format='%Y-%m-%d',
    )
    date_available_to = DateField(
        label='date_avalible_upto',
        default=datetime(2015, 1, 1, 23, 59, 59),
        format="%Y-%m-%d",
    )
    o_type = SelectField(
        'o_type',
        validators=[validators.DataRequired("Please choose company.")],
        choices=[
            ('daniednia', 'Danie dnia'),
            ('tygodniowe', 'Danie tygodniowe'),
            ('menu', 'Danie z menu'),
        ]
    )

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)


class DidUserPayForm(Form):
    """
    Did user Pay bool field
    """
    did_user_pay = SelectField(
        'did_user_pay',
        choices=[('1', 'Tak'), ('0', 'Nie')],
        default='0',
    )


class MailTextForm(Form):
    """
    Did user Pay bool field
    """
    daily_reminder = TextAreaField(
        "daily_reminder",
        validators=[validators.DataRequired(
            "Please enter daily reminder text."
        )]
    )
    monthly_pay_summary = TextAreaField(
        "monthly_pay_summary",
        validators=[validators.DataRequired(
            "Please enter monthly pay summary text."
        )]
    )
    pay_reminder = TextAreaField(
        "pay_reminder",
        validators=[validators.DataRequired(
            "Please enter pay reminder text."
        )]
    )
    pay_slacker_reminder = TextAreaField(
        "pay_slacker_reminder",
        validators=[validators.DataRequired(
            "Please enter pay reminder text for slackers."
        )]
    )


class UserDailyReminderForm(Form):
    """
    Did user Pay field
    """
    i_want_daily_reminder = BooleanField(
        'i_want_daily_reminder',
    )
