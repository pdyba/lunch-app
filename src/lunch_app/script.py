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

    def action_db_migrate(action=('a', 'start'), debug=False):
        from flask.ext.migrate import upgrade, init, migrate
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

    werkzeug.script.run()


if __name__ == '__main__' or __name__.startswith('uwsgi_file__'):
    application = make_app()
