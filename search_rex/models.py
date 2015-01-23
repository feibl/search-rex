from .core import db


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


class ActionType(object):
    view = 'view'
    copy = 'copy'


class Action(db.Model):
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
    __tablename__ = 'imported_record_similarity'

    from_record_id = db.Column(
        db.String(512), db.ForeignKey('record.record_id'),
        index=True, nullable=False, primary_key=True)

    to_record_id = db.Column(
        db.String(512), db.ForeignKey('record.record_id'),
        index=True, nullable=False, primary_key=True)

    similarity_value = db.Column(
        db.Float, nullable=False)
