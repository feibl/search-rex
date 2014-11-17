from search_rex.search_rec import compute_relevance
from search_rex.search_rec import compute_w_relevance


def test__compute_relevance__record_present():
    query_hits = {
        'doc1': 4,
        'doc2': 2,
        'doc3': 1,
        'doc4': 3,
    }
    assert compute_relevance('doc1', query_hits) == 0.4


def test__compute_relevance__record_not_present():
    query_hits = {
        'doc1': 4,
        'doc2': 2,
        'doc3': 1,
        'doc4': 3,
    }
    assert compute_relevance('unknown', query_hits) == 0.0


def test__compute_weighted_relevance__record_present():
    query_hit_rows = [
        {'doc1': 4, 'doc2': 2, 'doc3': 1, 'doc4': 3},
        {'doc3': 3, 'doc5': 7},
        {'doc1': 1, 'doc2': 5, 'doc5': 4},
    ]
    query_sims = [
        0.25,
        0.1,
        0.75,
    ]
    w_rel_doc1 = compute_w_relevance('doc1', query_hit_rows, query_sims)
    w_rel_doc2 = compute_w_relevance('doc2', query_hit_rows, query_sims)
    assert abs(w_rel_doc1 - 0.175) <= 0.00001
    assert abs(w_rel_doc2 - 0.425) <= 0.00001


def test__compute_weighted_relevance__record_not_present():
    query_hit_rows = [
        {'doc1': 4, 'doc2': 2, 'doc3': 1, 'doc4': 3},
        {'doc3': 3, 'doc5': 7},
        {'doc1': 1, 'doc2': 5, 'doc5': 4},
    ]
    query_sims = [
        0.25,
        0.1,
        0.75,
    ]
    w_rel_doc6 = compute_w_relevance('doc6', query_hit_rows, query_sims)
    assert w_rel_doc6 == 0.0
