from flask.ext.testing import TestCase
import os
from search_rex import app, db

_cwd = os.path.dirname(os.path.abspath(__file__))


class BaseTestCase(TestCase):
    '''
    The base-class for testing, sets up app and db,
    tears it down
    '''
    def create_app(self):
        '''
        Creates the app from the config-class TestConfiguration
        '''
        app.config.from_object('config.TestingConfig')
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
