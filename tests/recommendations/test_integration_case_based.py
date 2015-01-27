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
from search_rex.recommendations.recommenders.item_based import\
    AbstractRecordBasedRecommender
from search_rex.recommendations import Recommender
import os
from tests.resource.case_based_data import *


_cwd = os.path.dirname(os.path.abspath(__file__))


def create_recommender(include_internal_records):
    data_model = PersistentQueryDataModel(
        include_internal_records)
    in_mem_dm = InMemoryQueryDataModel(data_model)
    query_sim = AbstractQuerySimilarity()

    def get_similarity(from_query, to_query):
        if from_query in query_sims and to_query in query_sims[from_query]:
            return query_sims[from_query][to_query]
        return float('NaN')

    query_sim.get_similarity = get_similarity
    query_nhood = ThresholdQueryNeighbourhood(in_mem_dm, query_sim, 0.00001)
    query_based_recsys = QueryBasedRecommender(
        in_mem_dm, query_nhood, query_sim,
        WeightedSumScorer(Frequency()))

    return Recommender(AbstractRecordBasedRecommender(), query_based_recsys)


class QueryBasedRecommenderTestCase(BaseTestCase):

    def setUp(self):
        super(QueryBasedRecommenderTestCase, self).setUp()

    def test__recommend_search_results__exclude_internal_documents(self):
        views = view_matrix
        copies = copy_matrix
        include_internal_records = False

        import_test_data(views=views, copies=copies)

        sut = create_recommender(
            include_internal_records=include_internal_records)

        recs = sut.recommend_search_results(query_caesar)
        records = [rec.record_id for rec in recs]
        assert records == [record_caesar, record_brutus, record_cleopatra]

        recs = sut.recommend_search_results(query_brutus)
        records = [rec.record_id for rec in recs]
        assert records == [record_brutus, record_caesar]

        recs = sut.recommend_search_results(query_brutus_caesar)
        records = [rec.record_id for rec in recs]
        assert records == [record_caesar, record_brutus, record_cleopatra]

        recs = sut.recommend_search_results(query_caesar_secrets)
        records = [rec.record_id for rec in recs]
        assert records == [record_caesar, record_brutus, record_cleopatra]

        recs = sut.recommend_search_results(query_napoleon)
        records = [rec.record_id for rec in recs]
        assert records == [record_napoleon]

        # No similar query -> No recommendation
        recs = sut.recommend_search_results('unknown')
        records = [rec.record_id for rec in recs]
        assert records == []

        # Restrict to 2 recommendations
        recs = sut.recommend_search_results(query_caesar, max_num_recs=2)
        records = [rec.record_id for rec in recs]
        assert records == [record_caesar, record_brutus]

    def test__recommend_search_results__include_internal_documents(self):
        views = view_matrix
        copies = copy_matrix
        include_internal_records = True

        import_test_data(views=views, copies=copies)

        sut = create_recommender(
            include_internal_records=include_internal_records)

        recs = sut.recommend_search_results(query_caesar)
        records = [rec.record_id for rec in recs]
        assert records == [
            record_caesar_secrets, record_caesar, record_brutus,
            record_cleopatra]

        recs = sut.recommend_search_results(query_brutus)
        records = [rec.record_id for rec in recs]
        assert records == [record_brutus, record_caesar]

        recs = sut.recommend_search_results(query_brutus_caesar)
        records = [rec.record_id for rec in recs]
        assert records == [
            record_caesar, record_brutus, record_caesar_secrets,
            record_cleopatra]

        recs = sut.recommend_search_results(query_caesar_secrets)
        records = [rec.record_id for rec in recs]
        assert records == [
            record_caesar_secrets, record_caesar, record_brutus,
            record_cleopatra]

        recs = sut.recommend_search_results(query_napoleon)
        records = [rec.record_id for rec in recs]
        assert records == [record_napoleon]

        # No similar query -> No recommendation
        recs = sut.recommend_search_results('unknown')
        records = [rec.record_id for rec in recs]
        assert records == []

        # Restrict to 2 recommendations
        recs = sut.recommend_search_results(query_caesar, max_num_recs=2)
        records = [rec.record_id for rec in recs]
        assert records == [record_caesar_secrets, record_caesar]
