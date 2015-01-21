"""
Implements database queries that are used by the recommender system
"""

from ..models import Record
from ..models import Action
from ..models import SearchQuery
from ..models import ImportedRecordSimilarity
from ..core import db
from ..util.date_util import utcnow

from sqlalchemy.orm import aliased
import logging
from itertools import groupby


logger = logging.getLogger(__name__)


def get_actions_for_queries(
        include_internal_records, query_strings=None,
        max_age=None):
    """
    Retrieves the hit rows of the given queries
    """
    session = db.session

    query = session.query(
        Action.query_string, Action.time_created,
        Action.record_id, Action.action_type)
    query = query.join(Action.record)
    query = query.filter(
        Record.active == True)
    if query_strings:
        query = query.filter(
            Action.query_string.in_(query_strings)
        )
    else:
        query = query.filter(
            Action.query_string != None
        )
    if max_age:
        current_time = utcnow()
        min_time_created = current_time - max_age
        query = query.filter(Action.time_created >= min_time_created)
    if not include_internal_records:
        query = query.filter(Record.is_internal == False)
    query = query.order_by(Action.query_string)

    for query_string, actions in groupby(
            query, key=lambda action: action.query_string):
        yield (
            query_string, [
                action for action in actions
            ]
        )


def get_queries():
    '''Gets an iterator over all the committed queries'''
    session = db.session

    query = (
        session.query(SearchQuery.query_string).filter()
    )

    for query_string, in query:
        yield query_string


def get_records(include_internal_records):
    '''Gets an iterator over all the records'''
    session = db.session

    query = session.query(Record.record_id).filter(Record.active == True)
    if not include_internal_records:
        query = query.filter(Record.is_internal == False)

    for record_id, in query:
        yield record_id


def get_actions_of_session(session_id):
    """
    Retrieves the actions that have been recorded in the session
    """
    session = db.session

    query = session.query(Action)
    query = query.join(Action.record)
    query = query.filter(
        Action.session_id == session_id,
        Record.active == True).all()

    for action in query:
        yield action


def get_actions_on_record(record_id, max_age=None):
    """
    Retrieves the actions that have been performed on the record
    """
    session = db.session

    query = session.query(Action).filter(Action.record_id == record_id)
    if max_age:
        current_time = utcnow()
        min_time_created = current_time - max_age
        query = query.filter(Action.time_created >= min_time_created)

    for action in query:
        yield action


def get_actions_on_records(include_internal_records, max_age=None):
    """
    Retrieves the Records and the list of actions that have been performed
    on them
    """
    session = db.session

    query = session.query(Action)
    query = query.join(Action.record)
    query = query.filter(
        Record.active == True)
    if not include_internal_records:
        query = query.filter(Record.is_internal == False)
    if max_age:
        current_time = utcnow()
        min_time_created = current_time - max_age
        query = query.filter(Action.time_created >= min_time_created)
    query = query.order_by(Action.record_id)

    for record_id, actions in groupby(
            query, key=lambda action: action.record_id):
        yield (
            record_id, [
                action for action in actions
            ]
        )


def get_similarities(include_internal_records):
    session = db.session

    from_alias = aliased(Record)
    to_alias = aliased(Record)

    query = session.query(ImportedRecordSimilarity)
    query = query.join(
        from_alias,
        ImportedRecordSimilarity.from_record_id==from_alias.record_id)
    query = query.join(
        to_alias,
        ImportedRecordSimilarity.to_record_id==to_alias.record_id)

    query = query.filter(from_alias.active == True)
    query = query.filter(to_alias.active == True)
    if not include_internal_records:
        query = query.filter(from_alias.is_internal == False)
        query = query.filter(to_alias.is_internal == False)

    query = query.order_by(ImportedRecordSimilarity.from_record_id)

    for record_id, sims in groupby(
            query, key=lambda sim: sim.from_record_id):
        yield (
            record_id, {
                sim.to_record_id: sim.similarity_value
                for sim in sims
            }
        )
