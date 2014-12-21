from search_rex.recommendations.recommenders.item_based import\
    RecordBasedRecommender
from search_rex.recommendations.neighbourhood.item_based import\
    AbstractRecordNeighbourhood
from search_rex.recommendations.similarity.item_based import\
    AbstractRecordSimilarity
from search_rex.recommendations.data_model.item_based import\
    AbstractRecordBasedDataModel
import mock


session = 'bertha'

doc_caesar = 'caesar'
doc_brutus = 'brutus'
doc_rome = 'rome'
doc_cleopatra = 'cleopatra'
doc_napoleon = 'napoleon'

seen_docs = set([
    doc_caesar,
    doc_brutus,
])

doc_sims = {
    doc_caesar: {
        doc_brutus: 0.9,
        doc_cleopatra: 0.8,
        doc_rome: 0.5,
        doc_napoleon: 0.0,
    },
    doc_brutus: {
        doc_caesar: 0.9,
        doc_cleopatra: 0.2,
        doc_rome: 0.6,
        doc_napoleon: 0.0,
    },
}


def create_recommender(seen_docs=seen_docs, doc_sims=doc_sims):
    data_model = AbstractRecordBasedDataModel()
    data_model.get_seen_records = mock.Mock(
        side_effect=lambda s_id: seen_docs)
    record_sim = AbstractRecordSimilarity()
    record_sim.get_similarity = mock.Mock(
        side_effect=lambda from_id, to_id: doc_sims[from_id][to_id])
    record_nhood = AbstractRecordNeighbourhood()
    record_nhood.get_neighbours = mock.Mock(
        side_effect=lambda doc_id: doc_sims[doc_id].keys())

    return RecordBasedRecommender(
        data_model, record_nhood, record_sim)


def test__recommend__recommendations_ordered_by_score():
    sut = create_recommender()

    recs = sut.recommend(session, max_num_recs=10)
    assert recs == [(doc_rome, 1.1), (doc_cleopatra, 1.0), (doc_napoleon, 0.0)]


def test__recommend__max_num_recs_steers_amount_of_recs():
    sut = create_recommender()

    recs = sut.recommend(session, max_num_recs=2)
    assert recs == [(doc_rome, 1.1), (doc_cleopatra, 1.0)]


def test__recommend__no_seen_docs__empty_recs():
    sut = create_recommender(seen_docs=set())

    recs = sut.recommend(session, max_num_recs=10)
    assert recs == []


def test__recommend__no_neighbours_docs__empty_recs():
    sut = create_recommender(
        seen_docs=set([doc_caesar]), doc_sims={doc_caesar: {}})

    recs = sut.recommend(session, max_num_recs=10)
    assert recs == []


def test__recommend__estimation_for_doc_is_NaN__do_not_recommend_doc():
    sut = create_recommender(
        seen_docs=set([doc_caesar]),
        doc_sims={doc_caesar: {doc_napoleon: float('NaN')}}
    )

    recs = sut.recommend(session, max_num_recs=10)
    assert recs == []


def test__recommend__NaN_similarity_present__do_not_increase_estimation():
    sut = create_recommender(
        seen_docs=set([doc_caesar, doc_brutus]),
        doc_sims={
            doc_caesar: {doc_napoleon: float('NaN')},
            doc_brutus: {doc_napoleon: 0.5},
        }
    )

    recs = sut.recommend(session, max_num_recs=10)
    assert recs == [(doc_napoleon, 0.5)]
