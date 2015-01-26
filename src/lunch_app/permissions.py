# -*- coding: utf-8 -*-
"""
Permissions helpers
"""
from functools import wraps
from flask import flash
from flask.ext.restful import abort
from flask.ext.login import current_user
from flask.ext.admin.contrib.sqla import ModelView


def user_is_admin(func):
    """
    Wraper for if users is admin decorator
    """
    @wraps(func)
    def wrapped(*args, **kwargs):
        """
        Checks if users is admin decorator
        """
        if current_user.is_anonymous() or not current_user.is_admin():
            flash("You shell not pass")
            abort(401)
        else:
            return func(*args, **kwargs)
    return wrapped


class AdminModelViewWithAuth(ModelView):
    """
    ModelView with authentication.
    """

    def is_accessible(self):
        """
        Return True when user can access Admin.
        """
        return not current_user.is_anonymous() and current_user.is_admin()
