from test_base import BaseTestCase
from search_rex.recommender.data_model import PersistentDataModel
from search_rex.core import db
from datetime import datetime
from search_rex.recommender.models import Action
from search_rex.recommender.models import Record
from search_rex.recommender.models import ActionType
from search_rex.recommender.models import SearchQuery
from search_rex.recommender.models import SearchSession


class GetQueriesTestCase(BaseTestCase):

    def setUp(self):
        super(GetQueriesTestCase, self).setUp()

        self.data_model = PersistentDataModel(
            action_type=ActionType.view,
            include_internal_records=True)

    def test__get_queries(self):
        queries = ['hello', 'darkness', 'my', 'friend']
        session = db.session
        for q in queries:
            search_query = SearchQuery(query_string=q)
            session.add(search_query)
        session.commit()

        query_results = list(self.data_model.get_queries())
        assert len(query_results) == len(queries)
        assert sorted(query_results) == sorted(queries)


class GetHitsForQueryTestCase(BaseTestCase):

    def setUp(self):
        super(GetHitsForQueryTestCase, self).setUp()

    def test__internal_view__one_internal_view_action__hit_present(self):
        query_string = 'abc'
        record_id = 'doccc'

        sut = PersistentDataModel(
            action_type=ActionType.view,
            include_internal_records=True)
        sut.report_action(
            query_string=query_string, record_id=record_id,
            is_internal_record=True, session_id=1234,
            timestamp=datetime(1999, 1, 1))
        hit_rows = sut.get_hits_for_queries(
            [query_string])

        query_results = {
            query: hit_row for query, hit_row in hit_rows
        }

        assert len(query_results) == 1

    def test__internal_view__one_external_view_action__hit_present(self):
        query_string = 'abc'
        record_id = 'doccc'

        sut = PersistentDataModel(
            action_type=ActionType.view,
            include_internal_records=True)
        sut.report_action(
            query_string=query_string, record_id=record_id,
            is_internal_record=False, session_id=1234,
            timestamp=datetime(1999, 1, 1))
        hit_rows = sut.get_hits_for_queries(
            [query_string])

        query_results = {
            query: hit_row for query, hit_row in hit_rows
        }

        assert len(query_results) == 1

    def test__internal_view__only_copy_actions_present__no_hit(self):
        query_string = 'abc'
        record_id = 'doccc'

        sut = PersistentDataModel(
            action_type=ActionType.view,
            include_internal_records=True)
        copy_dm = PersistentDataModel(
            action_type=ActionType.copy,
            include_internal_records=True)
        copy_dm.report_action(
            query_string=query_string, record_id=record_id,
            is_internal_record=True, session_id=1234,
            timestamp=datetime(1999, 1, 1))
        hit_rows = sut.get_hits_for_queries(
            [query_string])

        query_results = {
            query: hit_row for query, hit_row in hit_rows
        }

        assert len(query_results) == 0

    def test__external_view__one_internal_view_action__no_hit(self):
        query_string = 'abc'
        record_id = 'doccc'

        sut = PersistentDataModel(
            action_type=ActionType.view,
            include_internal_records=False)
        sut.report_action(
            query_string=query_string, record_id=record_id,
            is_internal_record=True, session_id=1234,
            timestamp=datetime(1999, 1, 1))
        hit_rows = sut.get_hits_for_queries(
            [query_string])

        query_results = {
            query: hit_row for query, hit_row in hit_rows
        }

        assert len(query_results) == 0

    def test__external_view__one_external_view_action__hit_present(self):
        query_string = 'abc'
        record_id = 'doccc'

        sut = PersistentDataModel(
            action_type=ActionType.view,
            include_internal_records=False)
        sut.report_action(
            query_string=query_string, record_id=record_id,
            is_internal_record=False, session_id=1234,
            timestamp=datetime(1999, 1, 1))
        hit_rows = sut.get_hits_for_queries(
            [query_string])

        query_results = {
            query: hit_row for query, hit_row in hit_rows
        }

        assert len(query_results) == 1

    def test__external_view__only_copy_actions_present__no_hit(self):
        query_string = 'abc'
        record_id = 'doccc'

        sut = PersistentDataModel(
            action_type=ActionType.view,
            include_internal_records=False)
        copy_dm = PersistentDataModel(
            action_type=ActionType.copy,
            include_internal_records=True)
        copy_dm.report_action(
            query_string=query_string, record_id=record_id,
            is_internal_record=True, session_id=1234,
            timestamp=datetime(1999, 1, 1))
        hit_rows = sut.get_hits_for_queries(
            [query_string])

        query_results = {
            query: hit_row for query, hit_row in hit_rows
        }

        assert len(query_results) == 0


# class GetHitsForQueryTestCase(PersistentDmTestCase):
#
#     def setUp(self):
#         super(GetHitsForQueryTestCase, self).setUp()
#
#         self.query_string1 = 'query'
#         self.query_string2 = 'query2'
#         self.query_string3 = 'query3'
#         self.other_query = 'other_query'
#         self.doc1 = 'doc1'
#         self.doc2 = 'doc2'
#
#         self.hits = {
#             (self.query_string1, self.doc1): 2,
#             (self.query_string1, self.doc2): 1,
#             (self.query_string2, self.doc1): 1,
#             (self.query_string3, self.doc2): 1,
#             (self.other_query, self.doc1): 1,
#             (self.other_query, self.doc2): 1,
#         }
#
#         session_id = 0
#         for i, ((query_string, doc), hits) in enumerate(self.hits.iteritems()):
#             for j in range(hits):
#                 self.data_model.register_hit(
#                     query_string=query_string, community_id=TEST_COMMUNITY,
#                     record_id=doc, timestamp=datetime(1999, 1, 1),
#                     session_id=session_id)
#                 session_id += 1
#
#     def test__get_hits_for_query__one_query(self):
#         db_query = self.data_model.get_hits_for_queries(
#             [self.query_string1], community_id=TEST_COMMUNITY)
#
#         hit_rows = {
#             q_string: hit_row for q_string, hit_row in db_query
#         }
#         assert len(hit_rows) == 1
#         assert len(hit_rows[self.query_string1]) == 2
#         assert hit_rows[self.query_string1][self.doc1].total_hits == 2
#         assert hit_rows[self.query_string1][self.doc2].total_hits == 1
#
#     def test__get_hits_for_query__multiple_queries(self):
#         query_strings = [
#             self.query_string1,
#             self.query_string2,
#             self.query_string3
#         ]
#
#         db_query = self.data_model.get_hits_for_queries(
#             query_strings, community_id=TEST_COMMUNITY)
#
#         hit_rows = {
#             q_string: hit_row for q_string, hit_row in db_query
#         }
#
#         assert len(hit_rows) == 3
#         assert hit_rows[self.query_string1][self.doc1].total_hits == 2
#         assert hit_rows[self.query_string1][self.doc2].total_hits == 1
#         assert hit_rows[self.query_string2][self.doc1].total_hits == 1
#         assert hit_rows[self.query_string3][self.doc2].total_hits == 1
