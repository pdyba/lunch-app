# pylint: disable=missing-docstring
from wtforms import Form, validators, TextAreaField, IntegerField, BooleanField, \
    SelectField, DateField

from datetime import datetime, date


class OrderForm(Form):
    """
    New Order Creation Form
    """
    description = TextAreaField(
        "description",
        validators=[validators.DataRequired("Please enter order description.")]
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
    today_date = date.today()
    date = DateField(default=today_date, format='%Y-%m-%d')

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        """
        walidacja ewemntualna czy ta osoba cos juz zamowile tego dnia
        person = Person.query.filter_by(email=self.email.data.lower()).first()
        if person:
            self.email.errors.append("That email is already taken")
            return False
        else:
            return True
        """


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
    date_available = DateField(label='date_available', default=datetime(2015, 1, 1, 11, 1, 1), format='%Y-%m-%d')
    date_avalible_upto = DateField(label='date_avalible_upto', default=datetime(2015, 1, 1, 11, 1, 1), format="%Y-%m-%d")

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)