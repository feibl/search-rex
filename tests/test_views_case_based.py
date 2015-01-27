from test_base import BaseTestCase
from search_rex.recommendations.data_model.case_based import\
    InMemoryQueryDataModel
from search_rex.recommendations.data_model.case_based import\
    PersistentQueryDataModel
from search_rex.recommendations.neighbourhood.case_based import\
    ThresholdQueryNeighbourhood
from search_rex.recommendations.similarity.case_based import\
    AbstractQuerySimilarity
from search_rex.recommendations.recommenders.case_based import\
    QueryBasedRecommender
from search_rex.recommendations.recommenders.case_based import\
    WeightedSumScorer, Frequency
from search_rex.recommendations import create_recommender_system
from search_rex.recommendations import refresh_recommenders
import os
from tests.resource.case_based_data import *
from collections import namedtuple


_cwd = os.path.dirname(os.path.abspath(__file__))


class QuerySimilarity(AbstractQuerySimilarity):
    def __init__(self, query_sims):
        self.query_sims = query_sims

    def get_similarity(self, from_query, to_query):
        if from_query in query_sims:
            if to_query in self.query_sims[from_query]:
                return self.query_sims[from_query][to_query]
        return float('NaN')

    def refresh(self, refreshed_components):
        refreshed_components.add(self)


def create_query_recommender(include_internal_records):
    data_model = PersistentQueryDataModel(
        include_internal_records)
    in_mem_dm = InMemoryQueryDataModel(data_model)
    query_sim = QuerySimilarity(query_sims)

    query_nhood = ThresholdQueryNeighbourhood(in_mem_dm, query_sim, 0.00001)
    query_based_recsys = QueryBasedRecommender(
        in_mem_dm, query_nhood, query_sim,
        WeightedSumScorer(Frequency()))

    return query_based_recsys


base_url = '/api'


def create_request(route, parameters):
    return '{}?{}'.format(
        route,
        '&'.join(['{}={}'.format(k, v) for k, v in parameters.items()])
    )


class QueryBasedRecommenderTestCase(BaseTestCase):

    def setUp(self):
        super(QueryBasedRecommenderTestCase, self).setUp()
        create_recommender_system(
            self.app, query_based_recsys_factory=create_query_recommender)

    def recommend_search_results(
            self, query_string, include_internal_records,
            max_num_recs=10):
        client, app = self.client, self.app

        url = base_url + '/recommended_search_results'
        request = create_request(url, dict(
            query_string=query_string,
            include_internal_records=include_internal_records,
            api_key=app.config['API_KEY'],
            max_num_recs=max_num_recs)
        )
        rv = client.get(request)
        print(rv.json)
        Recommendation = namedtuple('Recommendation', ['record_id'])
        return [Recommendation(e['record_id']) for e in rv.json['results']]

    def test__recommend_search_results__exclude_internal_documents(self):
        views = view_matrix
        copies = copy_matrix
        include_internal_records = False

        def recommend_search_results(query_string, max_num_recs=10):
            return self.recommend_search_results(
                query_string, include_internal_records, max_num_recs)

        import_test_data(views=views, copies=copies)

        # Not Refreshed -> No recommendations
        recs = recommend_search_results(query_caesar)
        records = [rec.record_id for rec in recs]
        assert records == []

        refresh_recommenders()

        recs = recommend_search_results(query_caesar)
        records = [rec.record_id for rec in recs]
        assert records == [record_caesar, record_brutus, record_cleopatra]

        recs = recommend_search_results(query_brutus)
        records = [rec.record_id for rec in recs]
        assert records == [record_brutus, record_caesar]

        recs = recommend_search_results(query_brutus_caesar)
        records = [rec.record_id for rec in recs]
        assert records == [record_caesar, record_brutus, record_cleopatra]

        recs = recommend_search_results(query_caesar_secrets)
        records = [rec.record_id for rec in recs]
        assert records == [record_caesar, record_brutus, record_cleopatra]

        recs = recommend_search_results(query_napoleon)
        records = [rec.record_id for rec in recs]
        assert records == [record_napoleon]

        # No similar query -> No recommendation
        recs = recommend_search_results('unknown')
        records = [rec.record_id for rec in recs]
        assert records == []

        # Restrict to 2 recommendations
        recs = recommend_search_results(query_caesar, max_num_recs=2)
        records = [rec.record_id for rec in recs]
        assert records == [record_caesar, record_brutus]

    def test__recommend_search_results__include_internal_documents(self):
        views = view_matrix
        copies = copy_matrix
        include_internal_records = True

        def recommend_search_results(query_string, max_num_recs=10):
            return self.recommend_search_results(
                query_string, include_internal_records, max_num_recs)

        import_test_data(views=views, copies=copies)

        # Not Refreshed -> No recommendations
        recs = recommend_search_results(query_caesar)
        records = [rec.record_id for rec in recs]
        assert records == []

        refresh_recommenders()

        recs = recommend_search_results(query_caesar)
        records = [rec.record_id for rec in recs]
        assert records == [
            record_caesar_secrets, record_caesar, record_brutus,
            record_cleopatra]

        recs = recommend_search_results(query_brutus)
        records = [rec.record_id for rec in recs]
        assert records == [record_brutus, record_caesar]

        recs = recommend_search_results(query_brutus_caesar)
        records = [rec.record_id for rec in recs]
        assert records == [
            record_caesar, record_brutus, record_caesar_secrets,
            record_cleopatra]

        recs = recommend_search_results(query_caesar_secrets)
        records = [rec.record_id for rec in recs]
        assert records == [
            record_caesar_secrets, record_caesar, record_brutus,
            record_cleopatra]

        recs = recommend_search_results(query_napoleon)
        records = [rec.record_id for rec in recs]
        assert records == [record_napoleon]

        # No similar query -> No recommendation
        recs = recommend_search_results('unknown')
        records = [rec.record_id for rec in recs]
        assert records == []

        # Restrict to 2 recommendations
        recs = recommend_search_results(query_caesar, max_num_recs=2)
        records = [rec.record_id for rec in recs]
        assert records == [record_caesar_secrets, record_caesar]
