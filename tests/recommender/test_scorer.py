from search_rex.recommender.search_rec import relevance
from search_rex.recommender.search_rec import log_frequency
from search_rex.recommender.search_rec import WeightedScorer
from ..test_util import assert_almost_equal

from collections import namedtuple


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


def test__log_frequency__record_present():
    assert log_frequency(doc_1, query_hit_rows[query_1]) == 3.0


def test__log_frequency__record_not_present():
    assert log_frequency(ukn_doc, query_hit_rows[query_1]) == 0.0


def test__log_frequency__weight_is_zero():
    assert log_frequency(doc_1, {doc_1: 0.0, doc_2: 0.0}) == 0.0


def test__log_frequency__weight_is_negative():
    assert log_frequency(doc_1, {doc_1: -1.0, doc_2: 0.0}) == 0.0


def test__log_frequency__total_hit_row_is_empty():
    assert log_frequency(doc_1, {}) == 0.0


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
