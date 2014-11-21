from ..test_base import BaseTestCase
from search_rex.core import db
from search_rex.recommender.data_model import PersistentDataModel
from datetime import datetime
from search_rex.recommender.models import ResultClick
from search_rex.recommender.models import CommunityQuery
from search_rex.recommender.models import SearchQuery
from search_rex.recommender.models import SearchSession
from search_rex.recommender.models import Community


TEST_COMMUNITY = 'test_community'


class PersistentDmTestCase(BaseTestCase):

    def setUp(self):
        super(PersistentDmTestCase, self).setUp()
        self.data_model = PersistentDataModel()
        test_community = Community()
        test_community.community_id = TEST_COMMUNITY
        session = db.session
        session.add(test_community)
        session.commit()


class RegisterHitTestCase(PersistentDmTestCase):

    def setUp(self):
        super(RegisterHitTestCase, self).setUp()

        self.query_string = 'query'
        self.session_id = '1234'
        self.record_id = 'treehugging'
        self.t_stamp = datetime(1999, 11, 11)

        self.data_model.register_hit(
            query_string=self.query_string,
            community_id=TEST_COMMUNITY, record_id=self.record_id,
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
        query_results = list(self.data_model.get_queries(TEST_COMMUNITY))
        assert len(query_results) == len(self.queries)
        assert sorted(query_results) == sorted(self.queries)


class GetHitsForQueryTestCase(PersistentDmTestCase):

    def setUp(self):
        super(GetHitsForQueryTestCase, self).setUp()

        self.query_string1 = 'query'
        self.query_string2 = 'query2'
        self.query_string3 = 'query3'
        self.other_query = 'other_query'
        self.doc1 = 'doc1'
        self.doc2 = 'doc2'

        self.hits = {
            (self.query_string1, self.doc1): 2,
            (self.query_string1, self.doc2): 1,
            (self.query_string2, self.doc1): 1,
            (self.query_string3, self.doc2): 1,
            (self.other_query, self.doc1): 1,
            (self.other_query, self.doc2): 1,
        }

        session_id = 0
        for i, ((query_string, doc), hits) in enumerate(self.hits.iteritems()):
            for j in range(hits):
                self.data_model.register_hit(
                    query_string=query_string, community_id=TEST_COMMUNITY,
                    record_id=doc, t_stamp=datetime(1999, 1, 1),
                    session_id=session_id)
                session_id += 1

    def test__get_hits_for_query__one_query(self):
        hits_per_record = {
            record: hits for query_string, record, hits
            in self.data_model.get_hits_for_queries(
                [self.query_string1], community_id=TEST_COMMUNITY)
        }
        assert len(hits_per_record) == 2
        assert hits_per_record[self.doc1] == 2
        assert hits_per_record[self.doc2] == 1

    def test__get_hits_for_query__multiple_queries(self):
        hits_per_query = {
            (query_string, record): hits for query_string, record, hits
            in self.data_model.get_hits_for_queries(
                [self.query_string1, self.query_string2, self.query_string3],
                community_id=TEST_COMMUNITY)
        }
        assert len(hits_per_query) == 4
        assert hits_per_query[(self.query_string1, self.doc1)] == 2
        assert hits_per_query[(self.query_string1, self.doc2)] == 1
        assert hits_per_query[(self.query_string2, self.doc1)] == 1
        assert hits_per_query[(self.query_string3, self.doc2)] == 1
