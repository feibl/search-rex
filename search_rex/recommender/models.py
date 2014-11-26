from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKeyConstraint
from ..core import db
from sqlalchemy.sql.functions import GenericFunction
from sqlalchemy.types import Float
from sqlalchemy.ext.compiler import compiles


class hit_decay(GenericFunction):
    """
    An exponential decay function

    It is used for assigning older hits a lower weight
    :param hit_time: The time the hit occurred
    :param half_life: The number of days, the weight reaches the half of its
    initial weight
    :param life_span: The number of days, a hit is valid. Hits older than the
    life_span have a weight of 0
    """
    type = Float


@compiles(hit_decay, 'postgresql')
def pg_compile_hit_decay(element, compiler, **kw):
    if len(element.clauses) != 3:
        raise TypeError("hit_decay requires 3 parameters")
    hit_time, half_life, life_span = list(element.clauses)
    return (
        "CASE WHEN age(TIMEZONE('utc', CURRENT_TIMESTAMP), %s) "
        " > %s * interval '1 day' THEN 0.0 ELSE "
        " exp(-ln(2)/%s * floor("
        "  extract(epoch from age(TIMEZONE('utc', CURRENT_TIMESTAMP), %s))"
        "  / (3600 * 24)))"
        "END"
        )\
        % (
            compiler.process(hit_time),
            compiler.process(life_span),
            compiler.process(half_life),
            compiler.process(hit_time)
        )


@compiles(hit_decay, 'sqlite')
def sq_compile_hit_decay(element, compiler, **kw):
    if len(element.clauses) != 3:
        raise TypeError("hit_decay requires 3 parameters")
    # As sqlite is used for testing, definition of the decay is omitted
    return "1.0"


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

    session_id = db.Column(db.String(256), primary_key=True)
    time_created = db.Column(
        db.DateTime(), index=True, nullable=False)


class ResultClick(db.Model):
    __tablename__ = 'result_click'

    session_id = db.Column(
        db.String(256), db.ForeignKey('search_session.session_id'),
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
