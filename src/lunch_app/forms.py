from wtforms.ext.appengine.db import model_form
from wtforms import StringField, BooleanField, Form
from wtforms.validators import DataRequired, Length

from lunch_app.models import Order

class OrderForm:
    order_form = model_form(Order, Form)