from search_rex.query_sim import jaccard_sim, shingle


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


def test__jaccard_sim():
    set1 = [1, 2, 3, 4, 4]
    set2 = [1, 4, 5]

    assert jaccard_sim(set1, set2) == 0.4
