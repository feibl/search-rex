from models import Record
from models import Action
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
            timestamp, query_string=None):
        """
        Stores an action directed to a record
        """
        raise NotImplementedError()

    def get_hits_for_queries(self, query_strings, community_id):
        '''Retrieves the hit rows of the given queries'''
        raise NotImplementedError()

    def get_queries(self, community_id):
        '''Gets an iterator over all the committed queries'''
        raise NotImplementedError()

    def last_interaction_time(self, community_id, record_ids):
        '''Returns the time when someone has lately interacted with the
        records specified by their ids'''
        raise NotImplementedError()

    def popularity_rank(self, community_id, record_ids):
        '''Computes the popularity rank for the given records'''
        raise NotImplementedError()


class PersistentDataModel(DataModel):
    '''Stores the DataModel in a Database'''

    def __init__(
            self, action_type, include_internal_records,
            half_life=600, life_span=1200):
        self.action_type = action_type
        self.include_internal_records = include_internal_records
        self.half_life = half_life
        self.life_span = life_span

    def report_action(
            self, record_id, is_internal_record, session_id,
            timestamp, query_string=None):
        """
        Stores an action directed to a record
        """

        session = db.session

        action = Action.query.filter_by(
            session_id=session_id, record_id=record_id,
            action_type=self.action_type
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
            query_string=query_string, action_type=self.action_type,
            record_id=record_id
        )

        session.add(action)

        session.commit()
        return True

    def get_queries(self, community_id):
        '''Returns an iterator over all the queries committed by the
        community'''
        session = db.session
        self.is_community_present(session, community_id)

        query = (
            session.query(CommunityQuery.query_string)
            .filter(CommunityQuery.community_id == community_id)
        )

        for query_string, in query:
            yield query_string

    def get_hits_for_queries(self, query_strings, community_id):
        """
        Returns the query hit information

        To this belongs the query, record, record popularity, last interaction,
        overall hits and the adjusted hits
        """
        session = db.session
        self.is_community_present(session, community_id)

        query = (
            session.query(
                ResultClick.query_string,
                ResultClick.record_id,
                func.count().label('total_hits'),
                func.sum(func.hit_decay(
                    ResultClick.time_created, self.half_life,
                    self.life_span)
                ).label('decayed_hits'),
                func.max(ResultClick.time_created).label('last_interaction'),
                )
            .filter(
                ResultClick.community_id == community_id,
                ResultClick.query_string.in_(query_strings))
            .group_by(
                ResultClick.query_string,
                ResultClick.record_id)
            .order_by(
                ResultClick.query_string)
        )

        for q_string, group in groupby(query, key=lambda h: h.query_string):
            yield (
                q_string,
                {
                    hit.record_id: hit for hit in group
                }
            )

    def last_interaction_time(self, record_ids, community_id):
        query = (
            db.session.query(
                ResultClick.record_id,
                func.max(ResultClick.time_created))
            .filter(
                ResultClick.community_id == community_id,
                ResultClick.record_id.in_(record_ids))
            .group_by(ResultClick.record_id)
        )

        for record_id, last_interaction in query:
            yield (record_id, last_interaction)

    def popularity_rank(self, record_ids, community_id):
        query = (
            db.session.query(
                ResultClick.record_id,
                func.rank().over(
                    partition_by=ResultClick.record_id,
                    order_by=func.count().desc()))
            .filter(
                ResultClick.community_id == community_id,
                ResultClick.record_id.in_(record_ids))
            .group_by(ResultClick.record_id)
        )

        for record_id, rank in query:
            yield (record_id, rank)
