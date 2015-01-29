"""
The recommender system stores all the data, such as the actions and the
queries of the users, in a database. In this module the design of the database
is declared. This is done by defining models with the help of SQLAlchemy,
a Object Relational Mapper (ORM) for python. A model describes the essential
fields and behaviours of the data that is used in the application. Further,
each model represents a single database table.
"""

from .core import db


class SearchQuery(db.Model):
    """
    The query object represents a unique search query. It is identified by a
    query string.
    """
    __tablename__ = 'search_query'

    query_string = db.Column(
        db.Text(), index=True, primary_key=True, nullable=False)

    def __repr__(self):
        return '{0}: {1}'.format(self.__class__.__name__, self.query_string)


class SearchSession(db.Model):
    """
    A search session identifies a stay of a single user.
    It holds all the actions performed by the user during this period.
    """
    __tablename__ = 'search_session'

    session_id = db.Column(db.String(256), primary_key=True)
    time_created = db.Column(
        db.DateTime(), index=True, nullable=False)


class Record(db.Model):
    """
    A record is an entry of the catalogue application. It is the item to be
    recommended to the user by the recommender system. There are two types of
    different records: internal and external records. The former represents a
    record that is provided by the HSR. It can only be recommended to
    internal users. The latter is from an external source. It can be
    recommended to both external and internal users.
    """
    __tablename__ = 'record'

    record_id = db.Column(
        db.String(512), primary_key=True, index=True, nullable=False)
    active = db.Column(
        db.Boolean(), default=True, nullable=False)
    is_internal = db.Column(
        db.Boolean(), default=True, nullable=False)


class ActionType(object):
    """
    Defines the two action types: view and copy
    """
    view = 'view'
    copy = 'copy'


class Action(db.Model):
    """
    An action expresses an interaction of a user with a record. Two different
    types of actions are distinguished. The first one is the View Action.
    It indicates that the user has requested the detail view of a record.
    The second one is the Copy Action. It indicates that the user has
    copied the link to the geodata location. Both types of actions are only
    stored once per session and record. Further, the action may be the result
    of a previous query.
    """
    __tablename__ = 'action'

    record_id = db.Column(
        db.String(512), db.ForeignKey('record.record_id'),
        index=True, nullable=False, primary_key=True)

    session_id = db.Column(
        db.String(256), db.ForeignKey('search_session.session_id'),
        index=True, nullable=False, primary_key=True)

    action_type = db.Column(
        db.Enum(ActionType.view, ActionType.copy, name="action_types"),
        index=True, nullable=False, primary_key=True)

    query_string = db.Column(
        db.Text(), db.ForeignKey('search_query.query_string'),
        index=True, nullable=True)

    time_created = db.Column(
        db.DateTime(), index=True, nullable=False)

    record = db.relationship(Record, uselist=False)


class ImportedRecordSimilarity(db.Model):
    """
    The imported record similarity represents the similarity of a record to
    another record. The similarity, in this case, is a value that expresses
    how similar the two records are. Usually, the higher the similarity value
    is, the more similar are the two records. Moreover, it is normally in
    the range of 0 and 1, whereas the former value implies no while the latter
    implies complete similarity.

    The similarities to be imported are usually calculated by an external
    process. The recommender system then uses these similarities when
    generating recommendations. For this reason, they help the system in the
    case when no usage data is available.
    """
    __tablename__ = 'imported_record_similarity'

    from_record_id = db.Column(
        db.String(512), db.ForeignKey('record.record_id'),
        index=True, nullable=False, primary_key=True)

    to_record_id = db.Column(
        db.String(512), db.ForeignKey('record.record_id'),
        index=True, nullable=False, primary_key=True)

    similarity_value = db.Column(
        db.Float, nullable=False)
