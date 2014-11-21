from flask.ext.testing import TestCase
import os
from search_rex.database import db
from search_rex.factory import create_app

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
        app = create_app('config.TestingConfig')
        return app

    def setUp(self):
        db.drop_all()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
