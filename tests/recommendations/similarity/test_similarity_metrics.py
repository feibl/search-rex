from search_rex.recommendations.similarity.similarity_metrics import\
    jaccard_sim
from search_rex.recommendations.similarity.similarity_metrics import\
    cosine_sim
import math


def test__jaccard_sim():
    set1 = [1, 2, 3, 4, 4]
    set2 = [1, 4, 5]

    assert jaccard_sim(set1, set2) == 0.4


def test__jaccard_sim__one_list_is_empty():
    set1 = [1, 2]
    set2 = []

    assert jaccard_sim(set1, set2) == 0.0


def test__jaccard_sim__empty_sets():
    set1 = []
    set2 = []

    assert math.isnan(jaccard_sim(set1, set2)) is True


def test__cosine_sim():
    v1 = {'hello': 1.0, 'world': 2.0}
    v2 = {'world': 3.0, 'is': 4.0, 'hello': 1.0}

    assert abs(cosine_sim(v1, v2) - 0.6139) < 0.0001


def test__cosine_sim__one_vector_is_empty():
    v1 = {'hello': 1.0, 'world': 2.0}
    v2 = {}

    assert abs(cosine_sim(v1, v2) - 0.0) < 0.0001


def test__cosine_sim__both_vectors_are_empty():
    v1 = {}
    v2 = {}

    assert math.isnan(cosine_sim(v1, v2)) is True
