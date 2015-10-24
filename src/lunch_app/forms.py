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
    StringField,
    DateTimeField,
    SelectMultipleField,
    widgets,
)


FOOD_TYPE_LIST = ['pizza', 'burger', 'sushi', 'chinese', 'other']

class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = widgets.ListWidget(prefix_label=False, html_tag='ol')
    option_widget = widgets.CheckboxInput()


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
    )
    send_me_a_copy = BooleanField('send_me_a_copy', default=False)


class OrderEditForm(OrderForm):
    """
    New Order Eidt Form
    """
    user_name = StringField("user_name")
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
        format='%Y-%m-%d',
    )
    date_available_to = DateField(
        label='date_avalible_upto',
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
    daily_reminder_subject = StringField(
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
            "Please enter text which will be shown for blocked users"
        )]
    )
    ordering_is_blocked_text = TextAreaField(
        "ordering_is_blocked_text",
        validators=[validators.DataRequired(
            "Please enter text which will be shown if ordering is blocked"
        )]
    )


class UserPreferences(Form):
    """
    User daily reminder form.
    """
    i_want_daily_reminder = BooleanField(
        'i_want_daily_reminder',
    )
    preferred_arrival_time = SelectField(
        'preferred_arrival_time',
        choices=[
            ('12:00', '12:00'),
            ('13:00', '13:00'),
        ]
    )
    favourite_food = MultiCheckboxField(
        'preferred_arrival_time',
        choices=[(food,)*2 for food in FOOD_TYPE_LIST],
        validators=[validators.optional()]
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


class CompanyAddForm(Form):
    """
    Mail subject and text edit form.
    """
    name = StringField(
        "name",
        validators=[validators.DataRequired(
            "Please enter name."
        )]
    )
    web_page = StringField(
        "web_page",
        validators=[validators.DataRequired(
            "Please enter web site address."
        )]
    )
    address = TextAreaField(
        "address",
        validators=[validators.DataRequired(
            "Please enter address."
        )]
    )
    telephone = StringField(
        "telephone",
        validators=[validators.DataRequired(
            "Please enter pay reminder text."
        )]
    )


class FoodRateForm(Form):
    """
    Food rating form.
    """
    rater_best = chr(9829)
    rater_good = chr(9733)
    rater_medium = chr(10138)+chr(10136)+chr(10137)
    rater_bad = chr(9762)
    rater_worst = chr(9760)
    food = SelectField(
        'food',
        validators=[validators.DataRequired("Please choose food.")],
        coerce=int,
    )
    rate = SelectField(
        'rate',
        coerce=int,
        validators=[validators.DataRequired("Please rate.")],
        choices=[
            (1, 1*rater_worst),
            (2, 2*rater_bad),
            (3, rater_medium),
            (4, 4*rater_good),
            (5, 5*rater_best),
        ],
    )


class FinanceBlockUserForm(Form):
    """
    Finance block user form
    """
    user_select = SelectField(
        'user_select',
    )


class PizzaChooseForm(Form):
    """
    Choose a pizza
    """
    description = TextAreaField(
        "description",
        validators=[validators.DataRequired('Please enter your pizza.')],
    )
    pizza_size = SelectField(
        'pizza_size',
        validators=[validators.DataRequired("Please choose pizza size.")],
        choices=[
            ('small', 'small'),
            ('medium', 'medium'),
            ('big', 'big'),
        ]
    )


class CreateConflict(Form):
    """
    Create a conflict.
    """
    did_order_come = BooleanField(
        'did_order_come',
        validators=[validators.DataRequired("Please check if order come")],
    )
    i_know_who = BooleanField(
        'i_know_who',
    )
    user_connected = SelectField('user_connected', default=None)


class ResolveConflict(Form):
    """
    Resolve a conflict.
    """
    resolved = BooleanField(
        'resolved',
    )
    resolved_by = SelectField(
        'resolved_by',
    )
    notes = TextAreaField(
        "notes",
    )


class CreateFoodEventForm(Form):
    """
    Create food event.
    """
    event_name = StringField("event_name")
    food_type = SelectField(
        'food_type',
        validators=[validators.DataRequired("Please choose food type")],
        choices=[(food,)*2 for food in FOOD_TYPE_LIST],
    )
    other_food_type = StringField(
        "other_food_type",
        validators=[validators.Optional()],
    )
    food_company = StringField("food_company")
    menu = StringField("menu", validators=[
        validators.data_required(message="Please enter a menu link")
    ])
    deadline_for_ordering = DateTimeField(format='%H:%M')
    eta = DateTimeField(format='%H:%M')


class FoodEventChooseForm(Form):
    """
    Food event ordering form.
    """
    description = TextAreaField(
        "description",
        validators=[validators.DataRequired('Please enter your pizza.')],
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
