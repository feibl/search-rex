from search_rex.recommender.query_sim import shingle
from search_rex.recommender.query_sim import StringJaccardSimilarity


def test__shingle():
    input_string = '1234567'
    expected_shingles = set([
        '123',
        '234',
        '345',
        '456',
        '567',
    ])
    assert shingle(input_string, 3) == expected_shingles


def test__shingle__input_string_smaller_k():
    input_string = '12'
    assert shingle(input_string, 3) == set(['12'])


def test__string_jaccard_sim():
    string1 = 'hello'
    string2 = 'yellow'

    sut = StringJaccardSimilarity(k_shingles=3)

    assert sut.compute_similarity(string1, string2) == 0.4
