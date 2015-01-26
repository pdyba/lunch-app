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
    )
    cost = IntegerField(
        'cost',
        validators=[validators.DataRequired('Please enter your cost.')]
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
    today_date = datetime.now().replace(microsecond=0)
    date = DateField(default=today_date, format='%Y-%m-%d')


class OrderEditForm(OrderForm):
    """
    New Order Eidt Form
    """
    user_name = TextAreaField("description")


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
        validators=[validators.DataRequired('Please enter cost.')]
    )
    today_date = date.today()
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

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)