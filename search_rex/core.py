"""
This module provides the core elements such as the database object
"""

from flask.ext.sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class InvalidUsage(Exception):
    """
    An exception that indicates that the API is not used correctly

    This may occur if a required parameter is not provided by the caller
    """
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv
