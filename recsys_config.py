import os
import tempfile


basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI =\
        'postgresql://postgres:postgres@localhost/search_rex'
    API_KEY = '8ab9dc3f'
    # celery -A search_rex.tasks worker --loglevel=info --beat
    CELERY_BROKER_URL =\
        'sqla+postgresql://postgres:postgres@localhost/search_rex'


class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI =\
        'sqlite:///' + tempfile.gettempdir() + '/search_rex.db'
