from search_rex.recommendations.recommenders.case_based import relevance
from search_rex.recommendations.recommenders.case_based import LogFrequency
from search_rex.recommendations.recommenders.case_based import Frequency
from search_rex.recommendations.recommenders.case_based import WeightedScorer
from search_rex.recommendations.recommenders.case_based import\
    WeightedSumScorer
from search_rex.recommendations.recommenders.case_based import\
    QueryBasedRecommender
from search_rex.recommendations.data_model.case_based import\
    AbstractQueryDataModel
from search_rex.recommendations.similarity.case_based import\
    AbstractQuerySimilarity
from search_rex.recommendations.neighbourhood.case_based import\
    AbstractQueryNeighbourhood
from ...test_util import assert_almost_equal

from collections import namedtuple

import mock


Hit = namedtuple(
    'Hit',
    [
        'total_hits',
        'decayed_hits',
    ]
)


query_1 = 'query_1'
query_2 = 'query_2'
query_3 = 'query_3'

doc_1 = 'doc_1'
doc_2 = 'doc_2'
doc_3 = 'doc_3'
doc_4 = 'doc_4'
doc_5 = 'doc_5'

ukn_doc = 'unknown'

query_hit_rows = {
    query_1: {doc_1: 8, doc_2: 8, doc_3: 2, doc_4: 2},
    query_2: {doc_3: 16, doc_5: 4},
    query_3: {doc_1: 8, doc_2: 16, doc_5: 8},
}

query_sims = {
    query_1: 0.25,
    query_2: 0.1,
    query_3: 0.75,
}


def test__relevance__record_present():
    assert relevance(doc_1, query_hit_rows[query_1]) == 0.4


def test__relevance__record_not_present():
    assert relevance(ukn_doc, query_hit_rows[query_1]) == 0.0


def test__relevance__total_hits_is_zero():
    assert relevance(doc_1, {doc_1: 0.0, doc_2: 0.0}) == 0.0


def test__relevance__total_hit_row_is_empty():
    assert relevance(doc_1, {}) == 0.0


def test__frequency__record_present():
    sut = Frequency()
    hit_row = {doc_1: 8, doc_2: 1}
    assert sut(doc_1, hit_row) == 8.0


def test__frequency__record_not_present():
    sut = Frequency()
    hit_row = {doc_1: 8, doc_2: 1}
    assert sut(doc_3, hit_row) == 0.0


def test__frequency__empty_hit_row():
    sut = Frequency()
    hit_row = {}
    assert sut(doc_3, hit_row) == 0.0


def test__log_frequency__record_present():
    sut = LogFrequency(base=2, scale=1.0)
    hit_row = {doc_1: 8, doc_2: 1}
    assert sut(doc_1, hit_row) == 3.0


def test__log_frequency__base_10():
    sut = LogFrequency(base=10, scale=1.0)
    hit_row = {doc_1: 10, doc_2: 1}
    assert sut(doc_1, hit_row) == 1.0


def test__log_frequency__record_not_present():
    sut = LogFrequency(base=2, scale=1.0)
    hit_row = {doc_1: 8, doc_2: 1}
    assert sut(doc_3, hit_row) == 0.0


def test__log_frequency__weight_is_zero():
    sut = LogFrequency(base=2, scale=1.0)
    hit_row = {doc_1: 0.0, doc_2: 1.0}
    assert sut(doc_1, hit_row) == 0.0


def test__log_frequency__weight_is_negative():
    sut = LogFrequency(base=2, scale=1.0)
    hit_row = {doc_1: -1.0, doc_2: 1.0}
    assert sut(doc_1, hit_row) == 0.0


def test__log_frequency__scale_is_negative():
    sut = LogFrequency(base=2, scale=-1.0)
    hit_row = {doc_1: 1.0, doc_2: 1.0}
    assert sut(doc_1, hit_row) == 0.0


def test__log_frequency__total_hit_row_is_empty():
    sut = LogFrequency(base=2, scale=-1.0)
    hit_row = {}
    assert sut(doc_1, hit_row) == 0.0


def test__weighted_scorer():
    sut = WeightedScorer(lambda record, hit_row: 1.0)

    score = sut.compute_score(doc_1, query_hit_rows, query_sims)
    assert_almost_equal(score, 1.0, 0.00001)


def test__weighted_scorer__sims_are_zero():
    sut = WeightedScorer(lambda record, hit_row: 1.0)
    query_sims = {
        query_1: 0.0,
        query_2: 0.0,
        query_3: 0.0,
    }

    score = sut.compute_score(doc_1, query_hit_rows, query_sims)
    assert score == 0.0


def test__weighted_scorer__no_record():
    sut = WeightedScorer(lambda record, hit_row: 1.0)

    score = sut.compute_score(ukn_doc, query_hit_rows, query_sims)
    assert score == 0.0


def test__weighted_sum_scorer():
    sut = WeightedSumScorer(lambda record, hit_row: 1.0)

    score = sut.compute_score(doc_1, query_hit_rows, query_sims)
    assert_almost_equal(score, 1.0, 0.00001)


def test__weighted_sum_scorer__sims_are_zero():
    sut = WeightedSumScorer(lambda record, hit_row: 1.0)
    query_sims = {
        query_1: 0.0,
        query_2: 0.0,
        query_3: 0.0,
    }

    score = sut.compute_score(doc_1, query_hit_rows, query_sims)
    assert score == 0.0


def test__weighted_sum_scorer__no_record():
    sut = WeightedSumScorer(lambda record, hit_row: 1.0)

    score = sut.compute_score(ukn_doc, query_hit_rows, query_sims)
    assert score == 0.0


def test__q_recommender__refresh__underlying_components_are_refreshed():
    fake_model = AbstractQueryDataModel()
    fake_model.refresh = mock.Mock()
    fake_sim = AbstractQuerySimilarity()
    fake_sim.refresh = mock.Mock()
    fake_nhood = AbstractQueryNeighbourhood()
    fake_nhood.refresh = mock.Mock()

    sut = QueryBasedRecommender(
        data_model=fake_model,
        query_sim=fake_sim,
        query_nhood=fake_nhood,
        scorer=WeightedSumScorer(lambda r, hit_row: 1.0))

    refreshed_components = set()
    sut.refresh(refreshed_components)

    assert fake_model in refreshed_components
    assert fake_sim in refreshed_components
    assert fake_nhood in refreshed_components
    assert sut in refreshed_components
    assert fake_model.refresh.call_count == 1
    assert fake_sim.refresh.call_count == 1
    assert fake_nhood.refresh.call_count == 1
