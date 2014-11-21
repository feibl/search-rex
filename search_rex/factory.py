from flask import Flask
from core import db


def create_app(config_path=None):
    app = Flask(__name__)
    app.config.from_object(
        config_path if config_path else 'config.DevelopmentConfig')

    from recommender.controller import rec_api

    app.register_blueprint(rec_api)

    db.init_app(app)

    with app.app_context():
        from . import models
        db.create_all()

    return app
