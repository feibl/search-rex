from search_rex.recommender.similarity.item_based import\
    JaccardRecordSimilarity
import mock
import math


def test__get_similarity():
    record_1 = 'caesar'
    record_2 = 'brutus'
    interactions = {
        record_1: [1, 2, 3, 4, 4],
        record_2: [1, 4, 5],
    }

    fake_model = mock.Mock()
    fake_model.get_sessions_that_seen_record = mock.Mock(
        side_effect=lambda r: interactions[r])

    sut = JaccardRecordSimilarity(fake_model)

    assert sut.get_similarity(record_1, record_2) == 0.4


def test__get_similarity__one_list_is_empty():
    record_1 = 'caesar'
    record_2 = 'brutus'
    interactions = {
        record_1: [1, 2],
        record_2: [],
    }

    fake_model = mock.Mock()
    fake_model.get_sessions_that_seen_record = mock.Mock(
        side_effect=lambda r: interactions[r])

    sut = JaccardRecordSimilarity(fake_model)

    assert sut.get_similarity(record_1, record_2) == 0.0


def test__jaccard_sim__both_records_have_no_interactions__returns_nan():
    record_1 = 'caesar'
    record_2 = 'brutus'
    interactions = {
        record_1: [],
        record_2: [],
    }

    fake_model = mock.Mock()
    fake_model.get_sessions_that_seen_record = mock.Mock(
        side_effect=lambda r: interactions[r])

    sut = JaccardRecordSimilarity(fake_model)

    assert math.isnan(sut.get_similarity(record_1, record_2))
