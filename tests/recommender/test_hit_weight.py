from flask.ext.testing import TestCase
import os
from sqlalchemy import func
from search_rex.core import db
from search_rex.factory import create_app

from datetime import datetime
from datetime import timedelta

_cwd = os.path.dirname(os.path.abspath(__file__))


class HitDecayTestCase(TestCase):
    '''
    Test for the hit_decay function using the postgresql database
    '''
    def create_app(self):
        '''
        Creates the app using the production db
        '''
        app = create_app()
        return app

    def setUp(self):
        pass

    def tearDown(self):
        db.session.remove()

    def test__decayed_hit_weight__today__no_decay(self):
        hit_time = datetime.utcnow()
        half_life = 30
        life_span = 60
        result = db.session.query(
            func.hit_decay(hit_time, half_life, life_span))\
            .scalar()
        assert result == 1.0

    def test__decayed_hit_weight__older_than_life_span__no_weight(self):
        half_life = 30
        life_span = 60
        hit_time = datetime.utcnow() - timedelta(life_span + 1)
        result = db.session.query(
            func.hit_decay(hit_time, half_life, life_span))\
            .scalar()
        assert result == 0.0

    def test__decayed_hit_weight__half_life__half_weight(self):
        half_life = 30
        life_span = 60
        hit_time = datetime.utcnow() - timedelta(half_life)
        result = db.session.query(
            func.hit_decay(hit_time, half_life, life_span))\
            .scalar()
        assert result == 0.5
