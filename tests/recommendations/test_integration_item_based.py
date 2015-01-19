from test_base import BaseTestCase
from search_rex.recommendations.data_model.item_based import\
    InMemoryRecordDataModel
from search_rex.recommendations.data_model.item_based import\
    PersistentRecordDataModel
from search_rex.recommendations.neighbourhood.item_based import\
    KNearestRecordNeighbourhood
from search_rex.recommendations.similarity.item_based import\
    JaccardSimilarity
from search_rex.recommendations.similarity.item_based import\
    RecordSimilarity
from search_rex.recommendations.recommenders.item_based import\
    RecordBasedRecommender
from search_rex.recommendations import Recommender
import os
from tests.resource.item_based_data import *


_cwd = os.path.dirname(os.path.abspath(__file__))


def create_recommender(include_internal_records):
    data_model = PersistentRecordDataModel(
        include_internal_records)
    in_mem_dm = InMemoryRecordDataModel(data_model)
    pref_sim = JaccardSimilarity()
    record_sim = RecordSimilarity(in_mem_dm, pref_sim)
    record_nhood = KNearestRecordNeighbourhood(10, in_mem_dm, record_sim)
    record_based_recsys = RecordBasedRecommender(
        data_model, record_nhood, record_sim)

    return Recommender(record_based_recsys, None)


class RecordBasedRecommenderTestCase(BaseTestCase):

    def setUp(self):
        super(RecordBasedRecommenderTestCase, self).setUp()

    def test__inspired_by_your_history__exclude_internal_documents(self):
        views = view_actions
        copies = copy_actions
        include_internal_records = False

        import_test_data(views=views, copies=copies)

        sut = create_recommender(
            include_internal_records=include_internal_records)

        recs, _ = zip(*sut.recommend_from_history(session_alice))
        assert list(recs) == [record_cleopatra, record_napoleon]

        recs, _ = zip(*sut.recommend_from_history(session_bob))
        assert list(recs) == [record_napoleon]

        recs, _ = zip(*sut.recommend_from_history(session_carol))
        assert list(recs) == [record_caesar, record_brutus, record_napoleon]

        recs, _ = zip(*sut.recommend_from_history(session_dave))
        assert list(recs) == [record_brutus, record_cleopatra, record_napoleon]

        recs, _ = zip(*sut.recommend_from_history(
            session_dave, max_num_recs=2))
        assert list(recs) == [record_brutus, record_cleopatra]

        recs, _ = zip(*sut.recommend_from_history(session_eric))
        assert list(recs) == [
            record_caesar, record_brutus, record_cleopatra]

        # No Similar Records -> no recommendations
        recs = sut.recommend_from_history(session_isolated)
        assert list(recs) == []

        # Has seen all records -> no recommendations
        recs = sut.recommend_from_history(session_seen_all)
        assert list(recs) == []

        # Has seen no records -> no recommendations
        recs = sut.recommend_from_history(session_seen_nothing)
        assert list(recs) == []

    def test__inspired_by_your_history__include_internal_documents(self):
        views = view_actions
        copies = copy_actions
        include_internal_records = True

        import_test_data(views=views, copies=copies)

        sut = create_recommender(
            include_internal_records=include_internal_records)

        recs, _ = zip(*sut.recommend_from_history(session_alice))
        assert list(recs) == [
            record_cleopatra, record_secrets_of_rome, record_napoleon]

        recs, _ = zip(*sut.recommend_from_history(session_bob))
        assert list(recs) == [record_secrets_of_rome, record_napoleon]

        recs, _ = zip(*sut.recommend_from_history(session_carol))
        assert list(recs) == [
            record_caesar, record_brutus, record_secrets_of_rome,
            record_napoleon]

        recs, _ = zip(*sut.recommend_from_history(session_dave))
        assert list(recs) == [
            record_brutus, record_cleopatra, record_napoleon]

        recs, _ = zip(*sut.recommend_from_history(
            session_dave, max_num_recs=2))
        assert list(recs) == [record_brutus, record_cleopatra]

        recs, _ = zip(*sut.recommend_from_history(session_eric))
        assert list(recs) == [
            record_caesar, record_brutus, record_cleopatra,
            record_secrets_of_rome]

        # No Similar Records -> no recommendations
        recs = sut.recommend_from_history(session_isolated)
        assert list(recs) == []

        # Has seen all records -> no recommendations
        recs = sut.recommend_from_history(session_seen_all)
        assert list(recs) == []

        # Has seen no records -> no recommendations
        recs = sut.recommend_from_history(session_seen_nothing)
        assert list(recs) == []

    def test__similar_records__exclude_internal_documents(self):
        views = view_actions
        copies = copy_actions
        include_internal_records = False

        import_test_data(views=views, copies=copies)

        sut = create_recommender(
            include_internal_records=include_internal_records)

        recs, _ = zip(*sut.most_similar_records(record_welcome))
        assert list(recs) == [
            record_caesar, record_brutus, record_cleopatra,
            record_napoleon]

        recs, _ = zip(*sut.most_similar_records(record_caesar))
        assert list(recs) == [
            record_welcome, record_brutus, record_cleopatra,
            record_napoleon]

        recs, _ = zip(*sut.most_similar_records(record_caesar, max_num_recs=2))
        assert list(recs) == [
            record_welcome, record_brutus]

        recs, _ = zip(*sut.most_similar_records(record_brutus))
        assert list(recs) == [
            record_caesar, record_welcome, record_cleopatra,
            record_napoleon]

        recs = sut.most_similar_records(record_isolated)
        assert list(recs) == []

    def test__similar_records__include_internal_documents(self):
        views = view_actions
        copies = copy_actions
        include_internal_records = True

        import_test_data(views=views, copies=copies)

        sut = create_recommender(
            include_internal_records=include_internal_records)

        recs, _ = zip(*sut.most_similar_records(record_welcome))
        assert list(recs) == [
            record_caesar, record_brutus, record_cleopatra,
            record_secrets_of_rome, record_napoleon]

        recs, _ = zip(*sut.most_similar_records(record_caesar))
        assert list(recs) == [
            record_welcome, record_brutus, record_cleopatra,
            record_secrets_of_rome, record_napoleon]

        recs, _ = zip(*sut.most_similar_records(record_caesar, max_num_recs=2))
        assert list(recs) == [
            record_welcome, record_brutus]

        recs, _ = zip(*sut.most_similar_records(record_brutus))
        assert list(recs) == [
            record_caesar, record_welcome, record_cleopatra,
            record_napoleon, record_secrets_of_rome]

        recs = sut.most_similar_records(record_isolated)
        assert list(recs) == []
