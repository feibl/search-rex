from .test_base import BaseTestCase
from search_rex import db
from search_rex.data_model import PersistentDataModel
from datetime import datetime
from search_rex.models import ResultClick
from search_rex.models import CommunityQuery
from search_rex.models import SearchQuery
from search_rex.models import SearchSession


TEST_COMMUNITY = 'test_community'


class PersistentDmTestCase(BaseTestCase):

    def setUp(self):
        super(PersistentDmTestCase, self).setUp()
        self.data_model = PersistentDataModel(TEST_COMMUNITY)


class RegisterHitTestCase(PersistentDmTestCase):

    def setUp(self):
        super(RegisterHitTestCase, self).setUp()

        self.query_string = 'query'
        self.session_id = '1234'
        self.record_id = 'treehugging'
        self.t_stamp = datetime(1999, 11, 11)

        self.data_model.register_hit(
            query_string=self.query_string, record_id=self.record_id,
            t_stamp=self.t_stamp, session_id=self.session_id)

    def test__click_created(self):
        assert ResultClick.query.filter_by(
            query_string=self.query_string, session_id=self.session_id,
            record_id=self.record_id, time_created=self.t_stamp,
            community_id=TEST_COMMUNITY).one()

    def test__community_query_created(self):
        assert CommunityQuery.query.filter_by(
            query_string=self.query_string,
            community_id=TEST_COMMUNITY).one()

    def test__search_query_created(self):
        assert SearchQuery.query.filter_by(
            query_string=self.query_string).one()

    def test__search_session_created(self):
        assert SearchSession.query.filter_by(
            session_id=self.session_id,
            time_created=self.t_stamp).one()


class GetQueriesTestCase(PersistentDmTestCase):

    def setUp(self):
        super(GetQueriesTestCase, self).setUp()
        self.queries = ['hello', 'darkness', 'my', 'friend']
        session = db.session
        for q in self.queries:
            search_query = SearchQuery(query_string=q)
            comm_query = CommunityQuery(
                query_string=q, community_id=TEST_COMMUNITY)
            session.add(search_query)
            session.add(comm_query)
        session.commit()

    def test__get_queries(self):
        query_results = list(self.data_model.get_queries())
        assert len(query_results) == len(self.queries)
        assert sorted(query_results) == sorted(self.queries)
