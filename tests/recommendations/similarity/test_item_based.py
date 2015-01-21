from search_rex.recommendations.similarity.item_based import\
    JaccardSimilarity
from search_rex.recommendations.similarity.item_based import\
    CombinedRecordSimilarity
from search_rex.recommendations.similarity.item_based import\
    InMemoryRecordSimilarity
from search_rex.recommendations.similarity.item_based import\
    AbstractRecordSimilarity
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

from search_rex import services

import mock
import math
from datetime import timedelta
from datetime import datetime
from ..test_base import BaseTestCase


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


def test__combine_rec_similarity__get_similarity__underlying_sims_are_called():
    record_caesar = 'caesar'
    record_brutus = 'brutus'

    fake_sim1 = AbstractRecordSimilarity()
    fake_sim1.get_similarity = mock.Mock(return_value=0.8)
    fake_sim2 = AbstractRecordSimilarity()
    fake_sim2.get_similarity = mock.Mock(return_value=1.0)

    sut = CombinedRecordSimilarity(fake_sim1, fake_sim2, weight=0.25)
    sut.get_similarity(record_caesar, record_brutus)

    fake_sim1.get_similarity.assert_called_with(record_caesar, record_brutus)
    fake_sim2.get_similarity.assert_called_with(record_caesar, record_brutus)


def test__combine_rec_similarity__get_similarity():
    record_caesar = 'caesar'
    record_brutus = 'brutus'

    sims = []

    fake_sim1 = AbstractRecordSimilarity()
    fake_sim1.get_similarity = mock.Mock(
        side_effect=lambda f, t: sims[0])
    fake_sim2 = AbstractRecordSimilarity()
    fake_sim2.get_similarity = mock.Mock(
        side_effect=lambda f, t: sims[1])

    sut = CombinedRecordSimilarity(fake_sim1, fake_sim2, weight=0.25)

    sims = [0.8, 1.0]
    assert sut.get_similarity(record_caesar, record_brutus) == 0.95

    sims = [0.0, 1.0]
    assert sut.get_similarity(record_caesar, record_brutus) == 0.75

    sims = [float('nan'), 1.0]
    assert sut.get_similarity(record_caesar, record_brutus) == 0.75

    sims = [1.0, float('nan')]
    assert sut.get_similarity(record_caesar, record_brutus) == 0.25

    sims = [float('nan'), float('nan')]
    assert math.isnan(sut.get_similarity(record_caesar, record_brutus))


def test__combine_rec_similarity__refresh__underlying_sim_metrics_are_refreshed():
    fake_sim1 = AbstractRecordSimilarity()
    fake_sim1.refresh = mock.Mock()
    fake_sim2 = AbstractRecordSimilarity()
    fake_sim2.refresh = mock.Mock()

    sut = CombinedRecordSimilarity(fake_sim1, fake_sim2, weight=0.25)

    refreshed_components = set()
    sut.refresh(refreshed_components)

    assert fake_sim1 in refreshed_components
    assert fake_sim2 in refreshed_components
    assert sut in refreshed_components
    assert fake_sim1.refresh.call_count == 1
    assert fake_sim2.refresh.call_count == 1


class InMemorySimilarityTestCase(BaseTestCase):

    def setUp(self):
        super(InMemorySimilarityTestCase, self).setUp()

    def test__in_mem_sim__get_similarity(self):
        include_internal_records = False
        record_caesar = 'caesar'
        record_brutus = 'brutus'
        record_napoleon = 'napoleon'
        record_internal = 'internal'

        sims = {
            record_caesar: {
                record_brutus: 0.9,
                record_internal: 0.8,
            },
            record_brutus: {
                record_caesar: 0.8,
                record_internal: 0.7,
            },
            record_napoleon: {}
        }

        is_internal = {
            record_caesar: False,
            record_brutus: False,
            record_napoleon: False,
            record_internal: True,
        }

        for from_record, rec_sims in sims.iteritems():
            for to_record, sim in rec_sims.iteritems():
                services.import_record_similarity(
                    from_record, is_internal[from_record],
                    to_record, is_internal[to_record], sim)

        sut = InMemoryRecordSimilarity(
            include_internal_records=include_internal_records,
            max_sims_per_record=10)

        assert sut.get_similarity(record_caesar, record_brutus) ==\
            sims[record_caesar][record_brutus]
        assert sut.get_similarity(record_brutus, record_caesar) ==\
            sims[record_brutus][record_caesar]

        assert math.isnan(sut.get_similarity(record_caesar, record_napoleon))
        assert math.isnan(sut.get_similarity(record_napoleon, record_caesar))

        # Internal Record
        assert math.isnan(sut.get_similarity(record_caesar, record_internal))
        assert math.isnan(sut.get_similarity(record_internal, record_caesar))
        # Unknown Record
        assert math.isnan(sut.get_similarity('unknown', record_napoleon))
        assert math.isnan(sut.get_similarity(record_caesar, 'unknown'))

    def test__in_mem_sim__lower_similarities_are_discarded_if_max_sims_reached(self):
        record_caesar = 'caesar'
        record_brutus = 'brutus'
        record_napoleon = 'napoleon'
        record_cleopatra = 'cleopatra'

        sims = {
            record_caesar: {
                record_brutus: 0.9,
                record_cleopatra: 0.8,
                record_napoleon: 0.1,
            }
        }

        for from_record, rec_sims in sims.iteritems():
            for to_record, sim in rec_sims.iteritems():
                services.import_record_similarity(
                    from_record, False, to_record, False, sim)

        sut = InMemoryRecordSimilarity(
            include_internal_records=True, max_sims_per_record=2)

        assert math.isnan(sut.get_similarity(record_caesar, record_napoleon))

    def test__in_mem_sim__refresh__similarities_are_reloaded(self):
        record_caesar = 'caesar'
        record_brutus = 'brutus'

        sut = InMemoryRecordSimilarity(
            include_internal_records=True, max_sims_per_record=10)

        assert math.isnan(sut.get_similarity(record_caesar, record_brutus))

        sim = 0.9
        services.import_record_similarity(
            record_caesar, False, record_brutus, False, sim)

        refreshed_components = set()
        sut.refresh(refreshed_components)

        assert sut.get_similarity(record_caesar, record_brutus) == sim
        assert sut in refreshed_components


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

    assert abs(sim - 0.4228) < 0.0001


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
