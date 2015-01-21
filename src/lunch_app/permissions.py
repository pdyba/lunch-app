"""
Permissions helpers
"""
from functools import wraps
from flask import flash
from flask.ext.restful import abort
from werkzeug.utils import redirect
from flask.ext.login import current_user


def user_is_admin(f):
    """
    Checks if users is admin decorator
    """
    @wraps(f)
    def wrapped(*args, **kwargs):
        if current_user.is_anonymous() or not current_user.is_admin():
            flash("You shell not pass")
            abort(401)
        else:
            return f(*args, **kwargs)
    return wrapped
