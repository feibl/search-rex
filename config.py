import os


basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI =\
        'postgresql://postgres:postgres@localhost/search_rex'
    SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_search_rex')

    COMMUNITIES = set(['default', 'freaks', 'geeks'])
    DEFAULT_COMMUNITY = 'default'
    assert DEFAULT_COMMUNITY in COMMUNITIES


class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True


class TestingConfig(Config):
    TESTING = True
