from search_rex.recommendations.recommenders.item_based import\
    RecordBasedRecommender
from search_rex.recommendations.neighbourhood.item_based import\
    AbstractRecordNeighbourhood
from search_rex.recommendations.similarity.item_based import\
    AbstractRecordSimilarity
from search_rex.recommendations.data_model.item_based import\
    AbstractRecordDataModel
from search_rex.recommendations.data_model.item_based import\
    Preference
import mock
from datetime import datetime


session = 'bertha'

doc_caesar = 'caesar'
doc_brutus = 'brutus'
doc_rome = 'rome'
doc_cleopatra = 'cleopatra'
doc_napoleon = 'napoleon'

default_prefs = {
    doc_caesar: Preference(value=2.0, preference_time=datetime(1999, 1, 1)),
    doc_brutus: Preference(value=1.0, preference_time=datetime(1999, 1, 1)),
}

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


def create_recommender(preferences=default_prefs, doc_sims=doc_sims):
    data_model = AbstractRecordDataModel()
    data_model.get_preferences_of_session = mock.Mock(
        side_effect=lambda s_id: preferences)
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
    sut = create_recommender(preferences={})

    recs = sut.recommend(session, max_num_recs=10)
    assert recs == []


def test__recommend__no_neighbours_docs__empty_recs():
    preferences = {
        doc_caesar: Preference(2.0, datetime(1999, 1, 1)),
    }
    sut = create_recommender(
        preferences=preferences, doc_sims={doc_caesar: {}})

    recs = sut.recommend(session, max_num_recs=10)
    assert recs == []


def test__recommend__estimation_for_doc_is_NaN__do_not_recommend_doc():
    preferences = {
        doc_caesar: Preference(2.0, datetime(1999, 1, 1)),
    }
    sut = create_recommender(
        preferences=preferences,
        doc_sims={doc_caesar: {doc_napoleon: float('NaN')}}
    )

    recs = sut.recommend(session, max_num_recs=10)
    assert recs == []


def test__recommend__NaN_similarity_present__do_not_increase_estimation():
    preferences = {
        doc_caesar: Preference(2.0, datetime(1999, 1, 1)),
        doc_brutus: Preference(1.0, datetime(1999, 1, 1)),
    }
    sut = create_recommender(
        preferences=preferences,
        doc_sims={
            doc_caesar: {doc_napoleon: float('NaN')},
            doc_brutus: {doc_napoleon: 0.5},
        }
    )

    recs = sut.recommend(session, max_num_recs=10)
    assert recs == [(doc_napoleon, 0.5)]
