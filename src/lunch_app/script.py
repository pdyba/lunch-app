# -*- coding: utf-8 -*-
"""
Startup utilities.
"""
# pylint: disable=invalid-name, unused-variable

import os
import subprocess
from functools import partial
from logging.config import fileConfig

import werkzeug.script


etc = partial(os.path.join, 'parts', 'etc')

DEPLOY_INI = etc('deploy.ini')
DEPLOY_CFG = etc('deploy.cfg')

DEBUG_INI = etc('debug.ini')
DEBUG_CFG = etc('debug.cfg')


_buildout_path = os.getenv('BUILDOUT_DIRECTORY')
if not _buildout_path:
    _buildout_path = __file__
    for i in range(2 + __name__.count('.')):
        _buildout_path = os.path.dirname(_buildout_path)

abspath = partial(os.path.join, _buildout_path)
del _buildout_path


def make_app(global_cfg=None, cfg=DEPLOY_CFG, log_cfg=DEPLOY_INI, debug=False):
    """
    Create and configure Flask app.
    """
    global_cfg = {} if global_cfg is None else global_cfg
    fileConfig(log_cfg)
    from lunch_app.main import app, init
    app.config.from_pyfile(abspath(cfg))
    app.debug = debug
    init()
    return app


def make_debug(with_debug_layer=True, global_cfg=None, **conf):
    """
    Create and configure Flask app in debug mode.
    """
    global_cfg = {} if global_cfg is None else global_cfg
    from werkzeug.debug import DebuggedApplication
    app = make_app(global_cfg, cfg=DEBUG_CFG, log_cfg=DEBUG_INI, debug=True)
    if not with_debug_layer:
        return app
    return DebuggedApplication(app, evalex=True)


# bin/flask-ctl shell
def make_shell():
    """
    Interactive Flask Shell.
    """
    from flask import request
    app = make_app()
    http = app.test_client()
    reqctx = app.test_request_context
    return locals()


def _serve(action):
    """
    Build uWSGI command from 'action'.
    """
    argv = [abspath('bin', 'uwsgi')]

    if action in ('fg', 'start'):
        argv += ['--xml', abspath('parts', 'uwsgi', 'uwsgi.xml')]
    if action == 'start':
        argv += ['--daemonize', abspath('var', 'log', 'app.log')]
    if action in ('stop', 'reload'):
        argv += ['--' + action, abspath('var', 'pid', 'app.pid')]

    print(' '.join(argv))
    subprocess.call(argv)


# bin/flask-ctl ...
def run():
    """
    Main console script.
    """
    action_shell = werkzeug.script.make_shell(make_shell, make_shell.__doc__)
    action_debug = werkzeug.script.make_runserver(
        make_debug,
        use_reloader=True,
        hostname=os.getenv('IP', '0.0.0.0'),
        port=int(os.getenv('PORT', '8080')),
    )

    def action_serve(action=('a', 'start')):
        """Serve the application.
        This command serves a web application that uses a paste.deploy
        configuration file for the server and application.
        Options:
        - 'action' is one of [fg|start|stop|reload]
        """
        _serve(action)

    def action_init_db(debug=False):
        """Initialize database.
        Options:
        - '--debug' use debug configuration
        """
        if debug:
            make_debug()
        else:
            make_app()

        from .main import app, db
        from . import models
        db.create_all()

        sample_msg = 'Sample message'
        db.session.add(
            models.MailText(
                daily_reminder=sample_msg,
                daily_reminder_subject=sample_msg,
                monthly_pay_summary=sample_msg,
                pay_reminder=sample_msg,
                pay_slacker_reminder=sample_msg,
                info_page_text=sample_msg,
                blocked_user_text=sample_msg,
                ordering_is_blocked_text=sample_msg,
            ),
        )
        db.session.add(models.OrderingInfo(is_allowed=True))
        db.session.commit()

    def action_db_migrate(action=('a', 'start'), debug=False):
        """Migrate database.
        This command is responsible for data base migrations.
        Actions:
        init - initiates migration module use only once.
        migrate - creates schema migration.
        upgrade - upgrades database using schema migrations.

        Options:
        - '--debug' use debug configuration
        """
        from flask.ext.migrate import upgrade, init, migrate, stamp, downgrade
        if debug:
            app = make_debug(with_debug_layer=False)
        else:
            app = make_app()

        with app.app_context():
            if action == 'init':
                init()
            elif action == 'migrate':
                migrate()
            elif action == 'upgrade':
                upgrade()
            elif action == 'stamp':
                stamp()
            elif action == 'downgrade':
                downgrade()
            else:
                print('Unknown action')

    def action_send_daily_reminder(debug=False):
        """
        This command is responsible for sending every one an reminding
        e-mail that they did not ordered on current day at 10:45
        Options:
        - '--debug' use debug configuration
        """
        from .utils import send_daily_reminder

        if debug:
            app = make_debug(with_debug_layer=False)
        else:
            app = make_app()

        with app.app_context():
            send_daily_reminder()

    def action_add_tomas(debug=False):
        """
        This command is responsible for adding week menu from Tomas.
        use only on MONDAYS !
        Options:
        - '--debug' use debug configuration
        """
        from .utils import get_week_from_tomas

        if debug:
            app = make_debug(with_debug_layer=False)
        else:
            app = make_app()

        with app.app_context():
            get_week_from_tomas()

    def action_add_koziolek(debug=False):
        """
        This command is responsible for adding meal of a day from pod koziolek.
        use in the morning from Monday to Friday.
        Options:
        - '--debug' use debug configuration
        """
        from .utils import add_daily_koziolek

        if debug:
            app = make_debug(with_debug_layer=False)
        else:
            app = make_app()

        with app.app_context():
            add_daily_koziolek()

    def action_unblock_ordering(debug=False):
        """
        This command is responsible for blocking or unblocking the ability
        to create new orders. Use on 00:01 every day.
        Options:
        - '--debug' use debug configuration
        """
        from .utils import change_ordering_status

        if debug:
            app = make_debug(with_debug_layer=False)
        else:
            app = make_app()

        with app.app_context():
            change_ordering_status(True)

    def action_send_rate_reminder(debug=False):
        """
        This command is responsible for sending every one who ate an
        e-mail that they did not rated the meal on current day at 14:00
        Options:
        - '--debug' use debug configuration
        """
        from .utils import send_rate_reminder

        if debug:
            app = make_debug(with_debug_layer=False)
        else:
            app = make_app()

        with app.app_context():
            send_rate_reminder()

    werkzeug.script.run()


if __name__ == '__main__' or __name__.startswith('uwsgi_file__'):
    application = make_app()
