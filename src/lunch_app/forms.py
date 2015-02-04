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
    FloatField,
)

from datetime import datetime


class OrderForm(Form):
    """
    New Order Creation Form
    """

    description = TextAreaField(
        "description",
        validators=[validators.DataRequired('Please enter your order.')],
    )
    cost = FloatField(
        'cost',
        validators=[
            validators.DataRequired('Please enter cost.'),
            validators.NumberRange(
                min=0.01,
                max=999.99,
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
    cost = FloatField(
        'cost',
        validators=[
            validators.DataRequired('Please enter cost.'),
            validators.NumberRange(
                min=0.01,
                max=999.99,
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


class MailTextForm(Form):
    """
    Mail subject and text edit form.
    """
    daily_reminder_subject = TextAreaField(
        "daily_reminder_subject",
        validators=[validators.DataRequired(
            "Please enter daily reminder subject."
        )]
    )
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
    info_page_text = TextAreaField(
        "info_page_text",
        validators=[validators.DataRequired(
            "Please enter text for info page please start url with www or http"
        )]
    )
    blocked_user_text = TextAreaField(
        "blocked_user_text",
        validators=[validators.DataRequired(
            "Please enter text which will be shwon for blocked users"
        )]
    )


class UserDailyReminderForm(Form):
    """
    User daily reminder form.
    """
    i_want_daily_reminder = BooleanField(
        'i_want_daily_reminder',
    )


class FinanceSearchForm(Form):
    """
    Finance search form
    """
    year = IntegerField(
        'year',
        validators=[validators.DataRequired('Please enter your Year.')]
    )
    month = IntegerField(
        'month',
        validators=[validators.DataRequired('Please enter your Month.')]
    )
    did_pay = SelectField('did_pay', choices=[
        ('0', 'All'),
        ('1', 'Paid'),
        ('2', 'Unpaid'),
    ])


class FinanceBlockUserForm(Form):
    """
    Finance block user form
    """
    user_select = SelectField(
        'user_select',
    )
