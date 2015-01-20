from search_rex.recommendations.similarity.item_based import\
    JaccardSimilarity
from search_rex.recommendations.similarity.item_based import\
    CosineSimilarity
from search_rex.recommendations.similarity.item_based import\
    SignificanceWeighting
from search_rex.recommendations.similarity.item_based import\
    AbstractPreferenceSimilarity
from search_rex.recommendations.similarity.item_based import\
    RecordSimilarity
from search_rex.recommendations.similarity.item_based import\
    TimeDecaySimilarity
from search_rex.recommendations.similarity import item_based\
    as item_based_sim

from search_rex.recommendations.data_model.item_based import\
    Preference
from search_rex.recommendations.data_model.item_based import\
    AbstractRecordDataModel
import mock
import math
from datetime import timedelta
from datetime import datetime


def test__record_similarity__get_similarity():
    expected_sim = 1.0

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
    fake_sim = AbstractPreferenceSimilarity()
    fake_sim.get_similarity = mock.Mock(
        return_value=expected_sim)

    sut = RecordSimilarity(fake_model, fake_sim)
    sim = sut.get_similarity(record_1, record_2)

    assert sim == expected_sim
    fake_sim.get_similarity.assert_called_with(
        preferences[record_1],
        preferences[record_2])


def test__record_similarity__refresh__underlying_data_model_is_refreshed():
    fake_model = AbstractRecordDataModel()
    fake_model.refresh = mock.Mock()
    fake_sim = AbstractPreferenceSimilarity()

    sut = RecordSimilarity(fake_model, fake_sim)

    refreshed_components = set()
    sut.refresh(refreshed_components)

    assert fake_model in refreshed_components
    assert sut in refreshed_components
    assert fake_model.refresh.call_count == 1


def test__jaccard__get_similarity():
    from_prefs = {
        1: Preference(1.0, None),
        2: Preference(2.0, None),
        3: Preference(2.0, None),
        4: Preference(1.0, None),
    }
    to_prefs = {
        1: Preference(1.0, None),
        4: Preference(2.0, None),
        5: Preference(2.0, None),
    }

    sut = JaccardSimilarity()

    assert sut.get_similarity(from_prefs, to_prefs) == 0.4


def test__jaccard__get_similarity__one_list_is_empty():
    from_prefs = {
        1: Preference(1.0, None),
        2: Preference(2.0, None),
    }
    to_prefs = {}

    sut = JaccardSimilarity()

    assert sut.get_similarity(from_prefs, to_prefs) == 0.0


def test__jaccard_sim__both_records_have_no_interactions__returns_nan():
    from_prefs = {}
    to_prefs = {}

    sut = JaccardSimilarity()

    assert math.isnan(sut.get_similarity(from_prefs, to_prefs))


def test__cosine():
    from_prefs = {
        1: Preference(1.0, None),
        2: Preference(2.0, None),
    }
    to_prefs = {
        2: Preference(3.0, None),
        3: Preference(4.0, None),
        1: Preference(1.0, None),
    }

    sut = CosineSimilarity()

    assert abs(sut.get_similarity(from_prefs, to_prefs) - 0.6139) < 0.0001


def test__cosine__one_list_is_empty():
    from_prefs = {
        1: Preference(1.0, None),
        2: Preference(2.0, None),
    }
    to_prefs = {}

    sut = CosineSimilarity()

    assert sut.get_similarity(from_prefs, to_prefs) == 0.0


def test__cosine__both_records_have_no_interactions__returns_nan():
    from_prefs = {}
    to_prefs = {}

    sut = CosineSimilarity()

    assert math.isnan(sut.get_similarity(from_prefs, to_prefs))


def test__significance_weighting__below_min_overlap():
    min_overlap = 4
    sim = 1.0
    from_prefs = {
        1: Preference(1.0, None),
        2: Preference(2.0, None),
        3: Preference(2.0, None),
        4: Preference(1.0, None),
    }
    to_prefs = {
        1: Preference(1.0, None),
        2: Preference(2.0, None),
        5: Preference(2.0, None),
    }
    fake_sim = AbstractPreferenceSimilarity()
    fake_sim.get_similarity = mock.Mock(
        return_value=sim)

    sut = SignificanceWeighting(fake_sim, min_overlap)

    assert sut.get_similarity(from_prefs, to_prefs) == 0.5


def test__significance_weighting__above_min_overlap():
    min_overlap = 4
    sim = 1.0
    from_prefs = {
        1: Preference(1.0, None),
        2: Preference(2.0, None),
        3: Preference(2.0, None),
        4: Preference(1.0, None),
    }
    to_prefs = {
        1: Preference(1.0, None),
        2: Preference(2.0, None),
        3: Preference(2.0, None),
        4: Preference(1.0, None),
        5: Preference(2.0, None),
    }
    fake_sim = AbstractPreferenceSimilarity()
    fake_sim.get_similarity = mock.Mock(
        return_value=sim)

    sut = SignificanceWeighting(fake_sim, min_overlap)

    assert sut.get_similarity(from_prefs, to_prefs) == 1.0


def test__significance_weighting__similarity_is_nan():
    min_overlap = 4
    sim = float('NaN')
    from_prefs = {
        1: Preference(1.0, None),
        2: Preference(2.0, None),
        3: Preference(2.0, None),
        4: Preference(1.0, None),
    }
    to_prefs = {
        1: Preference(1.0, None),
        2: Preference(2.0, None),
        3: Preference(2.0, None),
        4: Preference(1.0, None),
        5: Preference(2.0, None),
    }
    fake_sim = AbstractPreferenceSimilarity()
    fake_sim.get_similarity = mock.Mock(
        return_value=sim)

    sut = SignificanceWeighting(fake_sim, min_overlap)

    assert math.isnan(sut.get_similarity(from_prefs, to_prefs))


def test__time_decay__similarity_is_weighted():
    fake_sim = AbstractPreferenceSimilarity()

    from_prefs = {
        1: Preference(1.0, datetime(2001, 12, 30)),
        2: Preference(2.0, datetime(2001, 12, 25)),
        3: Preference(2.0, datetime(2001, 12, 25)),
        4: Preference(1.0, datetime(2001, 12, 18)),
        5: Preference(1.0, datetime(2001, 12, 1)),
    }
    to_prefs = {
        1: Preference(1.0, datetime(2001, 12, 29)),
        2: Preference(2.0, datetime(2001, 12, 26)),
        4: Preference(1.0, datetime(2001, 12, 14)),
        5: Preference(1.0, datetime(2001, 11, 1)),
    }

    f_parts = [[1, 2, 3], [4], [], []]
    t_parts = [[1, 2], [], [4], []]

    def get_similarity(f_prefs, t_prefs):
        if f_prefs.keys() == f_parts[0] and t_prefs.keys() == t_parts[0]:
            return 0.8
        elif f_prefs.keys() == f_parts[1] and t_prefs.keys() == t_parts[1]:
            return 0.4
        elif f_prefs.keys() == f_parts[2] and t_prefs.keys() == t_parts[2]:
            return 0.0
        elif f_prefs.keys() == f_parts[3] and t_prefs.keys() == t_parts[3]:
            return float('nan')

    fake_sim.get_similarity = mock.Mock(
        side_effect=get_similarity)

    time_now = datetime(2001, 12, 31)
    item_based_sim.utcnow = mock.Mock(
        return_value=time_now)

    sut = TimeDecaySimilarity(
        fake_sim, time_interval=timedelta(7), half_life=2, max_age=4)

    sim = sut.get_similarity(from_prefs, to_prefs)

    assert abs(sim - 0.474445) < 0.00001


def test__time_decay__prefs_are_empty__return_nan():
    fake_sim = AbstractPreferenceSimilarity()

    from_prefs = {
    }
    to_prefs = {
    }

    fake_sim.get_similarity = mock.Mock(return_value=1.0)

    time_now = datetime(2001, 12, 31)
    item_based_sim.utcnow = mock.Mock(return_value=time_now)

    sut = TimeDecaySimilarity(
        fake_sim, time_interval=timedelta(7), half_life=2, max_age=4)

    sim = sut.get_similarity(from_prefs, to_prefs)

    assert math.isnan(sim)
