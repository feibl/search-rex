from flask.ext.testing import TestCase
import os
from flask import Flask
from search_rex.core import db
from search_rex.recommender.models import *

_cwd = os.path.dirname(os.path.abspath(__file__))


class BaseTestCase(TestCase):
    '''
    Sets up an arbitrary app
    '''
    def create_app(self):
        '''
        Creates the app from the config-class TestConfiguration
        '''
        app = Flask(__name__)
        app.config.from_object('config.TestingConfig')
        db.init_app(app)
        return app

    def setUp(self):
        db.drop_all()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
