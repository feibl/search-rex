import mock
from ..test_base import BaseTestCase
from search_rex.recommender.models import Community
from search_rex.recommender.data_model import PersistentDataModel
from search_rex.core import db
from search_rex.recommender.search_rec import GenericSearchResultRecommender
from search_rex.recommender.search_rec import WeightedSumScorer
from search_rex.recommender.search_rec import Frequency
from search_rex.recommender.query_sim import QuerySimilarity
from search_rex.recommender.query_nhood import ThresholdQueryNeighbourhood


import os
from datetime import datetime


_cwd = os.path.dirname(os.path.abspath(__file__))

TEST_COMMUNITY = 'test_community'


record_napoleon = 'Napoleon'
record_caesar = 'Julius Caesar'
record_caesar_salad = 'Caesar Salad'
record_asterix = 'Asterix'
record_brutus = 'Brutus'
record_gallia = 'Gallia'
record_cleopatra = 'Cleopatra'

query_caesar = 'caesar'
query_julius_caesar = 'julius caesar'
query_caesar_salad = 'caesar salad'
query_cleopatra = 'cleopatra'
query_napoleon = 'napoleon'
query_asterix = 'asterix'
query_obelix = 'obelix'
query_bonaparte = 'napoleon bonaparte'

query_santa = 'santa claus'

q_sims = {
    query_caesar: {
        query_caesar: 1.0,
        query_julius_caesar: 0.75,
        query_caesar_salad: 0.5,
    },
    query_julius_caesar: {
        query_julius_caesar: 1.0,
        query_caesar: 0.75,
        query_caesar_salad: 0.5,
    },
    query_asterix: {
        query_asterix: 1.0,
        query_obelix: 0.8,
    },
    query_obelix: {
        query_obelix: 1.0,
        query_asterix: 0.8,
    },
    query_cleopatra: {
        query_cleopatra: 1.0,
    },
    query_napoleon: {
        query_napoleon: 1.0,
    },
    query_caesar_salad: {
        query_caesar_salad: 1.0,
        query_julius_caesar: 0.5,
        query_caesar: 0.5,
    },
    query_santa: {
    },
    query_bonaparte: {
        query_napoleon: 0.75,
    }
}


def import_test_data(data_model):
    test_data_path = os.path.join(_cwd, 'resource', 'test_data.csv')
    with open(test_data_path, 'r') as td_file:
        lines = td_file.readlines()
        for i_line, line in enumerate(lines):
            line = line.strip()
            if i_line == 0:
                # Header
                continue
            if line == '':
                # Filler
                continue
            query, record, timestamp, session_id = line.split(',')
            timestamp = datetime.strptime(
                timestamp, '%Y-%m-%d %H:%M:%S')

            data_model.register_hit(
                query_string=query,
                record_id=record,
                t_stamp=timestamp,
                session_id=session_id,
                community_id=TEST_COMMUNITY)


def create_query_similarity():
    q_sim = QuerySimilarity()

    def compute_similarity(q1, q2, c_id):
        return q_sims[q1][q2] if q2 in q_sims[q1] else 0.0

    q_sim.compute_similarity = mock.Mock(side_effect=compute_similarity)
    return q_sim


def create_rec_system(data_model):
    d_model = PersistentDataModel()
    q_sim = create_query_similarity()
    q_nhood = ThresholdQueryNeighbourhood(
        data_model=d_model, query_sim=q_sim, sim_threshold=0.25)
    return GenericSearchResultRecommender(
        data_model=d_model,
        query_sim=q_sim,
        query_nhood=q_nhood,
        scorer=WeightedSumScorer(Frequency()))


class RecommendationTestCase(BaseTestCase):

    def create_community(self, community_id):
        test_community = Community()
        test_community.community_id = TEST_COMMUNITY
        session = db.session
        session.add(test_community)
        session.commit()

    def setUp(self):
        super(RecommendationTestCase, self).setUp()
        self.data_model = PersistentDataModel()
        self.create_community(TEST_COMMUNITY)

        import_test_data(self.data_model)
        self.sut = create_rec_system(self.data_model)

    def test__recommend__isolated_query__returns_1_recommendation(self):
        recs = self.sut.recommend(
            query_string=query_napoleon,
            community_id=TEST_COMMUNITY)

        assert len(recs) == 1
        assert recs[0].record_id == record_napoleon
        assert len(recs[0].related_queries) == 0

    def test__recommend__seen_query__current_query_is_set(self):
        recs = self.sut.recommend(
            query_string=query_napoleon,
            community_id=TEST_COMMUNITY)

        assert recs[0].current_query.query_string == query_napoleon

    def test__recommend__unseen_and_unrelated_query__no_recommendation(self):
        recs = self.sut.recommend(
            query_string=query_santa,
            community_id=TEST_COMMUNITY)

        assert len(recs) == 0

    def test__recommend__unseen_but_related_query__returns_recommendation(self):
        recs = self.sut.recommend(
            query_string=query_bonaparte,
            community_id=TEST_COMMUNITY)

        assert len(recs) == 1
        assert recs[0].record_id == record_napoleon
        assert len(recs[0].related_queries) == 1
        assert recs[0].related_queries[0].query_string == query_napoleon

    def test__recommend__unseen_but_related_query__current_query_is_none(self):
        recs = self.sut.recommend(
            query_string=query_bonaparte,
            community_id=TEST_COMMUNITY)

        assert recs[0].current_query is None

    def test__recommend__query_caesar(self):
        recs = self.sut.recommend(
            query_string=query_caesar,
            community_id=TEST_COMMUNITY)

        assert len(recs) == 6

    def test__recommend__query_caesar__recs_order(self):
        recs = self.sut.recommend(
            query_string=query_caesar,
            community_id=TEST_COMMUNITY)

        assert recs[0].record_id == record_caesar
        assert recs[1].record_id == record_cleopatra
        assert recs[2].record_id == record_brutus
        assert recs[3].record_id == record_asterix
        assert recs[4].record_id == record_gallia
        assert recs[5].record_id == record_caesar_salad