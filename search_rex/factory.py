from flask import Flask
from .core import db
from .models import *


def create_app(config_path=None):
    app = Flask(__name__)
    app.config.from_object(
        config_path if config_path else 'config.DevelopmentConfig')

    db.init_app(app)

    from api.recommender import rec_api

    app.register_blueprint(rec_api)

    return app
