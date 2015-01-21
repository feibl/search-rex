from .models import Record
from .models import Action
from .models import ActionType
from .models import SearchQuery
from .models import SearchSession
from .models import ImportedRecordSimilarity

import logging

from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound
from itertools import groupby

from .db_helper import get_one_or_create

from .core import db


logger = logging.getLogger(__name__)


class RecordNotPresentException(Exception):
    pass


def report_action(
        record_id, is_internal_record, session_id,
        timestamp, action_type, query_string=None):
    """
    Stores an action directed to a record
    """
    session = db.session

    action = Action.query.filter_by(
        session_id=session_id, record_id=record_id,
        action_type=action_type
    ).first()

    # Register the same click only once per session
    if action is not None:
        return True

    get_one_or_create(
        session, Record, record_id=record_id,
        create_kwargs={'is_internal': is_internal_record})
    if query_string:
        get_one_or_create(
            session, SearchQuery, query_string=query_string)
    get_one_or_create(
        session, SearchSession, session_id=session_id,
        create_kwargs={'time_created': timestamp})

    action = Action(
        session_id=session_id, time_created=timestamp,
        query_string=query_string, action_type=action_type,
        record_id=record_id
    )

    session.add(action)

    session.commit()
    return True


def report_view_action(
        record_id, is_internal_record, session_id,
        timestamp, query_string=None):
    """
    Stores a view action directed to a record
    """
    return report_action(
        record_id, is_internal_record, session_id, timestamp,
        ActionType.view, query_string)


def report_copy_action(
        record_id, is_internal_record, session_id,
        timestamp, query_string=None):
    """
    Stores a view action directed to a record
    """
    return report_action(
        record_id, is_internal_record, session_id, timestamp,
        ActionType.copy, query_string)


def set_record_active(record_id, active):
    """
    Sets a record active or inactive

    Inactive records are not returned in recommendations
    """
    record = Record.query.filter_by(record_id=record_id).first()
    if not record:
        raise RecordNotPresentException()

    record.active = active
    db.session.add(record)
    db.session.commit()
    return True


def import_record_similarity(
        from_record_id, from_is_internal, to_record_id, to_is_internal,
        similarity, max_sims_per_record=100):
    """
    Imports a similarity value from one record to the other
    """
    assert max_sims_per_record > 0
    created = False

    session = db.session
    get_one_or_create(
        session, Record, record_id=from_record_id,
        create_kwargs={'is_internal': from_is_internal})
    get_one_or_create(
        session, Record, record_id=to_record_id,
        create_kwargs={'is_internal': to_is_internal})

    sim = ImportedRecordSimilarity.query.filter_by(
        from_record_id=from_record_id,
        to_record_id=to_record_id).first()

    if sim:
        sim.similarity_value = similarity
        session.add(sim)
        created = True
    else:
        sim_to_create = ImportedRecordSimilarity()
        sim_to_create.from_record_id = from_record_id
        sim_to_create.to_record_id = to_record_id
        sim_to_create.similarity_value = similarity

        num_sims = ImportedRecordSimilarity.query.filter_by(
            from_record_id=from_record_id).count()

        if num_sims < max_sims_per_record:
            session.add(sim_to_create)
            created = True
        else:
            min_sim = ImportedRecordSimilarity.query.filter_by(
                from_record_id=from_record_id).order_by(
                    ImportedRecordSimilarity.similarity_value.asc()).first()

            if min_sim.similarity_value < similarity:
                session.delete(min_sim)
                session.add(sim_to_create)
                created = True

    session.commit()
    return created
