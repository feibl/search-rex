import datetime


def _utcnow():
    return datetime.datetime.utcnow()


def utcnow():
    return _utcnow()
