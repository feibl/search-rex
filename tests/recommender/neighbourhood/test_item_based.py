from search_rex.recommender.neighbourhood.item_based import\
    KNearestRecordNeighbourhood
from search_rex.recommender.similarity.item_based import\
    AbstractRecordSimilarity
import mock
import math


def create_k_nearest_neighbourhood(k, doc_sims, docs):
    fake_model = mock.Mock()
    fake_model.get_records = mock.Mock(
        return_value=docs)
    record_sim = AbstractRecordSimilarity()
    record_sim.get_similarity = mock.Mock(
        side_effect=lambda from_id, to_id: doc_sims[to_id])

    return KNearestRecordNeighbourhood(
        k=k, data_model=fake_model, record_sim=record_sim)


def test__get_nbours__target_record_is_not_returned():
    target_record = 'caesar'
    record_sims = {
        target_record: 1.0,
    }
    sut = create_k_nearest_neighbourhood(
        k=2, doc_sims=record_sims,
        docs=set([target_record]))

    assert set(sut.get_neighbours(target_record)) == set()


def test__get_nbours__more_than_k_possible_neighbours():
    target_record = 'caesar'
    record_1 = 'rome'
    record_2 = 'brutus'
    record_3 = 'cleopatra'
    record_sims = {
        target_record: 1.0,
        record_1: 1.0,
        record_2: 0.75,
        record_3: 0.5,
    }
    sut = create_k_nearest_neighbourhood(
        k=2, doc_sims=record_sims,
        docs=set([target_record, record_1, record_2, record_3]))

    assert set(sut.get_neighbours(target_record)) == set([record_1, record_2])

def test__get_nbours__less_than_k_possible_neighbours():
    target_record = 'caesar'
    record_1 = 'rome'
    record_2 = 'brutus'
    record_3 = 'cleopatra'
    record_sims = {
        target_record: 1.0,
        record_1: 1.0,
        record_2: 0.75,
        record_3: 0.5,
    }
    sut = create_k_nearest_neighbourhood(
        k=10, doc_sims=record_sims,
        docs=set([target_record, record_1, record_2, record_3]))

    assert set(sut.get_neighbours(target_record)) ==\
        set([record_1, record_2, record_3])


def test__get_nbours__records_having_nan_similarity_are_ignored():
    target_record = 'caesar'
    record_1 = 'rome'
    record_sims = {
        target_record: 1.0,
        record_1: float('NaN'),
    }
    sut = create_k_nearest_neighbourhood(
        k=10, doc_sims=record_sims,
        docs=record_sims.keys())

    assert set(sut.get_neighbours(target_record)) == set()
