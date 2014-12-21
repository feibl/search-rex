from search_rex.recommendations.similarity.similarity_metrics import\
    jaccard_sim
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
