"""
Permissions helpers
"""
from functools import wraps
from flask import flash
from werkzeug.utils import redirect
from flask.ext.login import current_user


def user_is_admin():
    """
    Checks if users is admin decorator
    """
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if current_user and not current_user.is_admin():
                flash("You shell not pass")
                return redirect('order')
            else:
                return f(*args, **kwargs)
        return wrapped
    return wrapper
