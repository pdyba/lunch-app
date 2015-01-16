# -*- coding: utf-8 -*-
"""
Flask app initialization.
"""
# pylint: disable=invalid-name

import datetime

from flask import Flask, g
from flask.ext import restful, login
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager, current_user
from flask.ext.admin import Admin
from flask.ext.admin.contrib.sqla import ModelView
from social.apps.flask_app.routes import social_auth
from social.apps.flask_app.template_filters import backends
from social.apps.flask_app.default.models import init_social


def init_social_login(app, db):
    app.register_blueprint(social_auth)
    init_social(app, db)

    login_manager = login.LoginManager()
    login_manager.login_view = 'index'
    login_manager.login_message = ''
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(userid):
        from . import models
        try:
            return models.User.query.get(id=userid)
        except (TypeError, ValueError):
            pass

    @app.before_request
    def global_user():
        g.user = login.current_user

    @app.context_processor
    def inject_user():
        try:
            return {'user': g.user}
        except AttributeError:
            return {'user': None}

    app.context_processor(backends)


def init_api(app):
    from . import resources
    api.add_resource(resources.Order, '/api/v1/order')


def init_admin():
    from . import models
    admin.add_view(ModelView(models.User, db.session))
    admin.add_view(ModelView(models.Order, db.session))

def init():
    init_social_login(app, db)
    init_api(app)
    init_admin()


app = Flask(__name__)
db = SQLAlchemy(app)
admin = Admin(app)
api = restful.Api(app)
