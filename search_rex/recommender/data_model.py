from models import Record
from models import Action
from models import ActionType
from models import SearchQuery
from models import SearchSession

import logging

from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound
from itertools import groupby

from ..db_helper import get_one_or_create

from ..core import db


logger = logging.getLogger(__name__)


class CommunityNotDefinedException(Exception):
    pass


class DataModel(object):
    '''This class stores the information about the queries and clicks committed
    by the different communities as well as the records'''

    def report_action(
            self, record_id, is_internal_record, session_id,
            timestamp, action_type, query_string=None):
        """
        Stores an action directed to a record
        """
        raise NotImplementedError()

    def report_view_action(
            self, record_id, is_internal_record, session_id,
            timestamp, query_string=None):
        """
        Stores a view action directed to a record
        """
        return self.report_action(
            record_id, is_internal_record, session_id, timestamp,
            ActionType.view, query_string)

    def report_copy_action(
            self, record_id, is_internal_record, session_id,
            timestamp, query_string=None):
        """
        Stores a view action directed to a record
        """
        return self.report_action(
            record_id, is_internal_record, session_id, timestamp,
            ActionType.copy, query_string)

    def get_hits_for_queries(
            self, query_strings, action_type, include_internal_records,
            half_life_in_days=150, life_span_in_days=300):
        '''Retrieves the hit rows of the given queries'''
        raise NotImplementedError()

    def get_queries(self):
        '''Gets an iterator over all the committed queries'''
        raise NotImplementedError()

    def get_records(self, include_internal_records):
        '''Gets an iterator over all the records'''
        raise NotImplementedError()

    def get_seen_records(self, session_id, action_type):
        """
        Retrieves the records that the session interacted with
        """
        raise NotImplementedError()

    def get_sessions_that_seen_record(self, record_id, action_type):
        """
        Retrieves the session that interacted with the record
        """
        raise NotImplementedError()


class PersistentDataModel(DataModel):
    '''Stores the DataModel in a Database'''
    def report_action(
            self, record_id, is_internal_record, session_id,
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

    def get_hits_for_queries(
            self, query_strings, action_type, include_internal_records,
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

    def get_queries(self):
        '''Gets an iterator over all the committed queries'''
        session = db.session

        query = (
            session.query(SearchQuery.query_string).filter()
        )

        for query_string, in query:
            yield query_string

    def get_records(self, include_internal_records):
        '''Gets an iterator over all the records'''
        session = db.session

        query = session.query(Record.record_id).filter()
        if not include_internal_records:
            query = query.filter(
                Record.is_internal == False)

        for record_id, in query:
            yield record_id

    def get_seen_records(self, session_id, action_type):
        """
        Retrieves the records that the session interacted with
        """
        session = db.session

        query = session.query(Action.record_id).filter(
            Action.action_type == action_type,
            Action.session_id == session_id)

        for record_id, in query:
            yield record_id

    def get_sessions_that_seen_record(self, record_id, action_type):
        """
        Retrieves the session that interacted with the record
        """
        session = db.session

        query = session.query(Action.session_id).filter(
            Action.record_id == record_id,
            Action.action_type == action_type)

        for session_id, in query:
            yield session_id


class AbstractActionDataModelWrapper(object):
    """
    A wrapper around a concrete DataModel whose methods do not include
    the action_type and the include_internal_records as parameters
    """

    def get_hits_for_queries(
            self, query_strings, half_life_in_days=150, life_span_in_days=300):
        '''Retrieves the hit rows of the given queries'''
        raise NotImplementedError()

    def get_records(self):
        '''Gets an iterator over all the records'''
        raise NotImplementedError()

    def get_queries(self):
        '''Gets an iterator over all the committed queries'''
        raise NotImplementedError()


class ActionDataModelWrapper(AbstractActionDataModelWrapper):
    """
    A wrapper around a concrete DataModel whose methods do not include
    the action_type and the include_internal_records as parameters

    The action_type and the include_internal_records are passed in the ctor
    """

    def __init__(
            self, data_model, action_type, include_internal_records):
        self.data_model = data_model
        self.action_type = action_type
        self.include_internal_records = include_internal_records

    def get_hits_for_queries(
            self, query_strings, half_life_in_days=150, life_span_in_days=300):
        '''Retrieves the hit rows of the given queries'''
        return self.data_model.get_hits_for_queries(
            query_strings=query_strings,
            half_life_in_days=half_life_in_days,
            life_span_in_days=life_span_in_days,
            action_type=self.action_type,
            include_internal_records=self.include_internal_records)

    def get_records(self):
        '''Gets an iterator over all the records'''
        return self.data_model.get_records(self.include_internal_records)

    def get_queries(self):
        '''Gets an iterator over all the committed queries'''
        return self.data_model.get_queries()

    def get_seen_records(self, session_id):
        """
        Retrieves the records that the session interacted with
        """
        return self.data_model.get_seen_records(
            session_id, self.action_type)

    def get_sessions_that_seen_record(self, record_id):
        """
        Retrieves the session that interacted with the record
        """
        return self.data_model.get_sessions_that_seen_record(
            record_id, self.action_type)
