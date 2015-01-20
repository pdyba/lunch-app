from functools import wraps
from flask import flash
from werkzeug.utils import redirect


def user_is_admin(user):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if user and not user.is_admin():
                flash("You shell not pass")
                return redirect('order')
            else:
                return f(*args, **kwargs)
        return wrapped
    return wrapper
