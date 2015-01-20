from search_rex.util.math_util import exp_decay
from datetime import timedelta
from datetime import datetime
from tests.test_util import assert_almost_equal


def test__exp_decay():
    v1 = exp_decay(
        4, datetime(2000, 1, 8), datetime(2000, 1, 4), timedelta(days=1),
        half_life=1, max_age=8)
    assert_almost_equal(v1, 0.25, 0.00001)


def test__exp_decay__half_life():
    v1 = exp_decay(
        4, datetime(2000, 1, 8), datetime(2000, 1, 7), timedelta(days=1),
        half_life=1, max_age=8)
    assert_almost_equal(v1, 2.0, 0.00001)


def test__exp_decay__older_than_max_age():
    v1 = exp_decay(
        4, datetime(2000, 1, 8), datetime(2000, 1, 4), timedelta(days=1),
        half_life=1, max_age=2)
    assert_almost_equal(v1, 0.0, 0.00001)


def test__exp_decay__t_equals_t0__weight_1():
    v1 = exp_decay(
        4.0, datetime(2000, 1, 8), datetime(2000, 1, 8), timedelta(days=1),
        half_life=1, max_age=2)
    assert_almost_equal(v1, 4.0, 0.00001)


def test__exp_decay__earlier_than_t0__weight_1():
    v1 = exp_decay(
        4.0, datetime(2000, 1, 8), datetime(2000, 1, 9), timedelta(days=1),
        half_life=1, max_age=2)
    assert_almost_equal(v1, 4.0, 0.00001)
