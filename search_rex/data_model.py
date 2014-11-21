from models import CommunityQuery
from models import Community
from models import Record
from models import ResultClick
from models import SearchQuery
from models import SearchSession

from sqlalchemy import func

from db_helper import get_one_or_create

from database import db


class DataModel(object):
    '''This class stores the information about the queries and clicks committed
    by the different communities as well as the records'''

    def register_hit(
            self, query_string, record_id, t_stamp, session_id):
        '''Stores a click on a search result recorded during the given
        session'''
        raise NotImplementedError()

    def get_hits_for_queries(self, query_strings):
        '''Retrieves the hit rows of the given queries'''
        raise NotImplementedError()

    def get_queries(self):
        '''Gets an iterator over all the committed queries'''
        raise NotImplementedError()

    def last_interaction_time(self, record_ids):
        '''Returns the time when someone has lately interacted with the
        records specified by their ids'''
        raise NotImplementedError()

    def popularity_rank(self, record_ids):
        '''Computes the popularity rank for the given records'''
        raise NotImplementedError()


class PersistentDataModel(DataModel):
    '''Stores the DataModel in a Database'''

    def __init__(self, community_id):
        self.community_id = community_id
        # session = db.session
        # get_one_or_create(
        #     session, Community, community_id=community_id)
        # session.commit()

    def register_hit(
            self, query_string, record_id, t_stamp, session_id):
        '''Stores a click on a search result recorded during the given
        session'''

        session = db.session

        result_click = ResultClick.query.filter_by(
            session_id=session_id, record_id=record_id,
            community_id=self.community_id, query_string=query_string
        ).first()

        # Register the same click only once per session
        if result_click is not None:
            return True

        get_one_or_create(
            session, Record, record_id=record_id)
        get_one_or_create(
            session, SearchQuery, query_string=query_string)
        get_one_or_create(
            session, CommunityQuery, query_string=query_string,
            community_id=self.community_id)
        get_one_or_create(
            session, SearchSession, session_id=session_id,
            create_kwargs={'time_created': t_stamp})

        result_click = ResultClick(
            session_id=session_id, time_created=t_stamp,
            community_id=self.community_id, query_string=query_string,
            record_id=record_id
        )

        session.add(result_click)

        session.commit()
        return True

    def get_queries(self):
        '''Returns an iterator over all the queries committed by the
        community'''
        query = (
            db.session.query(CommunityQuery.query_string)
            .filter(CommunityQuery.community_id == self.community_id)
        )

        for query_string, in query:
            yield query_string

    def get_hits_for_queries(self, query_strings):
        query = (
            db.session.query(
                ResultClick.query_string,
                ResultClick.record_id,
                func.count(ResultClick.query_string))
            .filter(
                ResultClick.community_id == self.community_id,
                ResultClick.query_string.in_(query_strings))
            .group_by(
                ResultClick.query_string,
                ResultClick.record_id)
            .order_by(
                ResultClick.query_string)
        )

        for query_string, record_id, count in query:
            yield (query_string, record_id, count)

    def last_interaction_time(self, record_ids):
        query = (
            db.session.query(
                ResultClick.record_id,
                func.max(ResultClick.time_created))
            .filter(
                ResultClick.community_id == self.community_id,
                ResultClick.record_id.in_(record_ids))
            .group_by(ResultClick.record_id)
        )

        for record_id, last_interaction in query:
            yield (record_id, last_interaction)

    def popularity_rank(self, record_ids):
        query = (
            db.session.query(
                ResultClick.record_id,
                func.rank().over(
                    partition_by=ResultClick.record_id,
                    order_by=func.count().desc()))
            .filter(
                ResultClick.community_id == self.community_id,
                ResultClick.record_id.in_(record_ids))
            .group_by(ResultClick.record_id)
        )

        for record_id, rank in query:
            yield (record_id, rank)
