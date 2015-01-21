from flask import Flask
from .core import db
from .models import *
from celery import Celery


def create_app(config_path=None):
    app = Flask(__name__)
    app.config.from_object(
        config_path if config_path else 'config.DevelopmentConfig')

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
