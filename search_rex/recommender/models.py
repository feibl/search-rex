from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKeyConstraint
from ..core import db


class Community(db.Model):
    __tablename__ = 'community'

    community_id = db.Column(
        db.String(256), primary_key=True, index=True, nullable=False)

    def __repr__(self):
        return '{0}: {1}'.format(self.__class__.__name__, self.community_id)


class SearchQuery(db.Model):
    __tablename__ = 'search_query'

    query_string = db.Column(db.Text(), primary_key=True, nullable=False)

    def __repr__(self):
        return '{0}: {1}'.format(self.__class__.__name__, self.query_string)


class CommunityQuery(db.Model):
    __tablename__ = 'community_query'

    community_id = db.Column(
        db.String(256), db.ForeignKey('community.community_id'),
        primary_key=True, index=True, nullable=False)

    query_string = db.Column(
        db.Text(), db.ForeignKey('search_query.query_string'),
        primary_key=True, index=True, nullable=False)


class Record(db.Model):
    __tablename__ = 'record'

    record_id = db.Column(
        db.Text(), primary_key=True, index=True, nullable=False)
    activated = db.Column(
        db.Boolean(), default=True, nullable=False)


class SearchSession(db.Model):
    __tablename__ = 'search_session'

    session_id = db.Column(db.Integer, primary_key=True)
    time_created = db.Column(
        db.DateTime(), index=True, nullable=False)


class ResultClick(db.Model):
    __tablename__ = 'result_click'

    session_id = db.Column(
        db.Integer, db.ForeignKey('search_session.session_id'),
        index=True, nullable=False, primary_key=True)
    query_string = db.Column(
        db.Text(), index=True, nullable=False, primary_key=True)
    community_id = db.Column(
        db.String(256), index=True, nullable=False, primary_key=True)
    record_id = db.Column(
        db.Text(), db.ForeignKey('record.record_id'),
        index=True, nullable=False, primary_key=True)
    time_created = db.Column(
        db.DateTime(), index=True, nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(
            [query_string, community_id],
            [CommunityQuery.query_string, CommunityQuery.community_id]), {})

    community_query = relationship('CommunityQuery')
    record = relationship('Record')
