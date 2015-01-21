<<<<<<< HEAD
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
=======
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
        if current_user and current_user.is_anonymous \
                or not current_user.is_admin():
            flash("You shell not pass")
            abort(401)
        else:
            return f(*args, **kwargs)
    return wrapped
>>>>>>> origin/master
