from search_rex.recommendations.similarity.item_based import\
    JaccardRecordSimilarity
from search_rex.recommendations.data_model.item_based import\
    AbstractRecordDataModel
from search_rex.recommendations.data_model.item_based import\
    Preference
import mock
import math


def test__get_similarity():
    record_1 = 'caesar'
    record_2 = 'brutus'
    preferences = {
        record_1: {
            1: Preference(1.0, None),
            2: Preference(2.0, None),
            3: Preference(2.0, None),
            4: Preference(1.0, None),
        },
        record_2: {
            1: Preference(1.0, None),
            4: Preference(2.0, None),
            5: Preference(2.0, None),
        },
    }

    fake_model = AbstractRecordDataModel()
    fake_model.get_preferences_for_record = mock.Mock(
        side_effect=lambda r: preferences[r])

    sut = JaccardRecordSimilarity(fake_model)

    assert sut.get_similarity(record_1, record_2) == 0.4


def test__get_similarity__one_list_is_empty():
    record_1 = 'caesar'
    record_2 = 'brutus'

    preferences = {
        record_1: {
            1: Preference(1.0, None),
            2: Preference(2.0, None),
        },
        record_2: {
        },
    }

    fake_model = AbstractRecordDataModel()
    fake_model.get_preferences_for_record = mock.Mock(
        side_effect=lambda r: preferences[r])

    sut = JaccardRecordSimilarity(fake_model)

    assert sut.get_similarity(record_1, record_2) == 0.0


def test__jaccard_sim__both_records_have_no_interactions__returns_nan():
    record_1 = 'caesar'
    record_2 = 'brutus'

    preferences = {
        record_1: {
        },
        record_2: {
        },
    }

    fake_model = AbstractRecordDataModel()
    fake_model.get_preferences_for_record = mock.Mock(
        side_effect=lambda r: preferences[r])

    sut = JaccardRecordSimilarity(fake_model)

    assert math.isnan(sut.get_similarity(record_1, record_2))
