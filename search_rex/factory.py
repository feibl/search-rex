"""
In this module, the function for instantiating the Flask application is
defined. To this function a configuration file is passed in which the
settings are provided that are used for creating the application.
"""

from flask import Flask
from .core import db
from .models import *
from celery import Celery


def create_app(config_path=None):
    """
    Factory method of the Flask application object

    param config_path: The path to the configuration file, or else a
    configuration object.
    """
    app = Flask(__name__)
    app.config.from_object(
        config_path if config_path else 'recsys_config.DevelopmentConfig')

    db.init_app(app)

    from .views import rec_api

    app.register_blueprint(rec_api)

    return app


def create_celery_app(app=None, config_path=None):
    app = app or create_app(config_path)
    celery = Celery(__name__, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery
