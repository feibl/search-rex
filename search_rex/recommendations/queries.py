"""
Implements database queries that are used by the recommender system
"""

from ..models import Record
from ..models import Action
from ..models import ActionType
from ..models import SearchQuery
from ..models import SearchSession

import logging

from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound
from itertools import groupby

from ..db_helper import get_one_or_create

from ..core import db


logger = logging.getLogger(__name__)


def get_hits_for_queries(
        query_strings, action_type, include_internal_records,
        half_life_in_days=150, life_span_in_days=300):
    """
    Retrieves the hit rows of the given queries
    """

    session = db.session
    query = session.query(
        Action.query_string,
        Action.record_id,
        func.count().label('total_hits'),
        func.sum(func.hit_decay(
            Action.time_created, half_life_in_days,
            life_span_in_days)
        ).label('decayed_hits'),
        func.max(Action.time_created).label('last_interaction'),
    )
    query = query.join(Action.record)
    query = query.filter(
        Action.action_type == action_type,
        Action.query_string.in_(query_strings)
    )

    if not include_internal_records:
        query = query.filter(
            Record.is_internal == False)

    query = query.group_by(
        Action.query_string, Action.record_id)
    query = query.order_by(Action.query_string)

    for q_string, group in groupby(query, key=lambda h: h.query_string):
        yield (
            q_string,
            {
                hit.record_id: hit for hit in group
            }
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


def get_actions_on_record(record_id):
    """
    Retrieves the actions that have been performed on the record
    """
    session = db.session

    query = session.query(Action).filter(Action.record_id == record_id)

    for action in query:
        yield action


def get_actions_on_records(include_internal_records):
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
    query = query.order_by(Action.record_id)

    for record_id, actions in groupby(
            query, key=lambda action: action.record_id):
        yield (
            record_id, [
                action for action in actions
            ]
        )
