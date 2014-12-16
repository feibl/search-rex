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


class SearchQuery(db.Model):
    __tablename__ = 'search_query'

    query_string = db.Column(
        db.Text(), index=True, primary_key=True, nullable=False)

    def __repr__(self):
        return '{0}: {1}'.format(self.__class__.__name__, self.query_string)


class SearchSession(db.Model):
    __tablename__ = 'search_session'

    session_id = db.Column(db.String(256), primary_key=True)
    time_created = db.Column(
        db.DateTime(), index=True, nullable=False)


class Record(db.Model):
    __tablename__ = 'record'

    record_id = db.Column(
        db.String(512), primary_key=True, index=True, nullable=False)
    active = db.Column(
        db.Boolean(), default=True, nullable=False)
    is_internal = db.Column(
        db.Boolean(), default=True, nullable=False)


class Action(db.Model):
    __tablename__ = 'action'

    record_id = db.Column(
        db.String(512), db.ForeignKey('record.record_id'),
        index=True, nullable=False, primary_key=True)

    session_id = db.Column(
        db.String(256), db.ForeignKey('search_session.session_id'),
        index=True, nullable=False, primary_key=True)

    action_type = db.Column(
        db.Enum("view", "copy", name="action_types"),
        index=True, nullable=False, primary_key=True)

    query_string = db.Column(
        db.Text(), db.ForeignKey('search_query.query_string'),
        index=True, nullable=True)

    time_created = db.Column(
        db.DateTime(), index=True, nullable=False)


class ImportedRecordSimilarity(db.Model):
    __tablename__ = 'imported_record_similarity'

    from_record_id = db.Column(
        db.String(512), db.ForeignKey('record.record_id'),
        index=True, nullable=False, primary_key=True)

    to_record_id = db.Column(
        db.String(512), db.ForeignKey('record.record_id'),
        index=True, nullable=False, primary_key=True)

    similarity_value = db.Column(
        db.Float, nullable=False)
