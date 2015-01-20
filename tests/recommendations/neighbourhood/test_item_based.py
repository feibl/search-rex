from search_rex.recommendations.neighbourhood.item_based import\
    KNearestRecordNeighbourhood
from search_rex.recommendations.neighbourhood.item_based import\
    InMemoryRecordNeighbourhood
from search_rex.recommendations.neighbourhood.item_based import\
    AbstractRecordNeighbourhood
from search_rex.recommendations.similarity.item_based import\
    AbstractRecordSimilarity
from search_rex.recommendations.data_model.item_based import\
    AbstractRecordDataModel
import mock
import math


def create_k_nearest_neighbourhood(k, doc_sims, docs):
    fake_model = AbstractRecordDataModel()
    fake_model.get_records = mock.Mock(
        return_value=docs)
    record_sim = AbstractRecordSimilarity()
    record_sim.get_similarity = mock.Mock(
        side_effect=lambda from_id, to_id: doc_sims[to_id])

    return KNearestRecordNeighbourhood(
        k=k, data_model=fake_model, record_sim=record_sim)


def test__knn__get_nbours__target_record_is_not_returned():
    target_record = 'caesar'
    record_sims = {
        target_record: 1.0,
    }
    sut = create_k_nearest_neighbourhood(
        k=2, doc_sims=record_sims,
        docs=set([target_record]))

    assert set(sut.get_neighbours(target_record)) == set()


def test__knn__get_nbours__more_than_k_possible_neighbours():
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


def test__knn__get_nbours__less_than_k_possible_neighbours():
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


def test__knn__get_nbours__records_having_nan_similarity_are_ignored():
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


def test__knn__get_nbours__records_having_0_similarity_are_ignored():
    target_record = 'caesar'
    record_1 = 'rome'
    record_sims = {
        target_record: 1.0,
        record_1: 0.0,
    }
    sut = create_k_nearest_neighbourhood(
        k=10, doc_sims=record_sims,
        docs=record_sims.keys())

    assert set(sut.get_neighbours(target_record)) == set()


def test__knn__refresh__underlying_data_model_and_similarity_is_refreshed():
    fake_model = AbstractRecordDataModel()
    fake_model.refresh = mock.Mock()
    fake_sim = AbstractRecordSimilarity()
    fake_sim.refresh = mock.Mock()

    sut = KNearestRecordNeighbourhood(5, fake_model, fake_sim)

    refreshed_components = set()
    sut.refresh(refreshed_components)

    assert fake_model in refreshed_components
    assert fake_sim in refreshed_components
    assert sut in refreshed_components
    assert fake_model.refresh.call_count == 1
    assert fake_sim.refresh.call_count == 1


def test__in_mem_knn__refresh__underlying_data_model_and_similarity_is_refreshed():
    fake_model = AbstractRecordDataModel()
    fake_model.get_records = mock.Mock(return_value=[])
    fake_model.refresh = mock.Mock()
    fake_sim = AbstractRecordSimilarity()
    fake_sim.get_similarity = mock.Mock(return_value=1.0)
    fake_sim.refresh = mock.Mock()
    fake_nhood = AbstractRecordNeighbourhood()
    fake_nhood.get_neighbours = mock.Mock(return_value=[])

    sut = InMemoryRecordNeighbourhood(
        fake_model, fake_sim, 50,
        nhood_factory=lambda dm, sim, num_nh: fake_nhood)

    sut = InMemoryRecordNeighbourhood(fake_model, fake_sim, 50)

    refreshed_components = set()
    sut.refresh(refreshed_components)

    assert fake_model in refreshed_components
    assert fake_sim in refreshed_components
    assert sut in refreshed_components
    assert fake_model.refresh.call_count == 1
    assert fake_sim.refresh.call_count == 1


def test__in_mem_knn__get_nbours():
    record_caesar = 'caesar'
    record_brutus = 'brutus'
    record_napoleon = 'napoleon'

    nbours = {
        record_caesar: [
            record_brutus
        ],
        record_brutus: [
            record_caesar
        ],
        record_napoleon: []
    }
    sims = {
        record_caesar: {
            record_brutus: 0.9
        },
        record_brutus: {
            record_caesar: 0.8
        },
        record_napoleon: {}
    }

    fake_model = AbstractRecordDataModel()
    fake_model.get_records = mock.Mock(return_value=nbours.keys())
    fake_sim = AbstractRecordSimilarity()
    fake_sim.get_similarity = mock.Mock(
        side_effect=lambda from_r, to_r: sims[from_r][to_r])
    fake_nhood = AbstractRecordNeighbourhood()
    fake_nhood.get_neighbours = mock.Mock(
        side_effect=lambda r: nbours[r])

    sut = InMemoryRecordNeighbourhood(
        fake_model, fake_sim, 50,
        nhood_factory=lambda dm, sim, num_nh: fake_nhood)

    assert sut.get_neighbours(record_caesar) == nbours[record_caesar]
    assert sut.get_neighbours(record_brutus) == nbours[record_brutus]
    assert sut.get_neighbours(record_napoleon) == nbours[record_napoleon]

    assert sut.get_neighbours('unknown') == []

    assert sut.get_similarity(record_caesar, record_brutus) ==\
        sims[record_caesar][record_brutus]
    assert sut.get_similarity(record_brutus, record_caesar) ==\
        sims[record_brutus][record_caesar]

    assert math.isnan(sut.get_similarity(record_caesar, record_napoleon))
    assert math.isnan(sut.get_similarity(record_napoleon, record_caesar))

    assert math.isnan(sut.get_similarity('unknown', record_napoleon))
    assert math.isnan(sut.get_similarity(record_caesar, 'unknown'))


def test__in_mem_knn__refres__data_is_reloaded():
    record_caesar = 'caesar'
    record_brutus = 'brutus'

    nbours = {
    }
    sims = {
    }

    fake_model = AbstractRecordDataModel()
    fake_model.get_records = mock.Mock(
        side_effect=lambda: nbours.keys())
    fake_model.refresh = mock.Mock()
    fake_sim = AbstractRecordSimilarity()
    fake_sim.get_similarity = mock.Mock(
        side_effect=lambda from_r, to_r: sims[from_r][to_r])
    fake_sim.refresh = mock.Mock()
    fake_nhood = AbstractRecordNeighbourhood()
    fake_nhood.get_neighbours = mock.Mock(
        side_effect=lambda r: nbours[r])

    sut = InMemoryRecordNeighbourhood(
        fake_model, fake_sim, 50,
        nhood_factory=lambda dm, sim, num_nh: fake_nhood)

    assert sut.get_neighbours(record_caesar) == []
    assert math.isnan(sut.get_similarity(record_caesar, record_brutus))

    nbours[record_caesar] = [record_brutus]
    nbours[record_brutus] = [record_caesar]
    sims[record_caesar] = {record_brutus: 0.9}
    sims[record_brutus] = {record_caesar: 0.8}

    sut.refresh(set())

    assert sut.get_neighbours(record_caesar) == nbours[record_caesar]
    assert sut.get_similarity(record_caesar, record_brutus) ==\
        sims[record_caesar][record_brutus]
