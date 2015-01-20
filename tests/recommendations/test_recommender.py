from search_rex.recommendations.recommenders.item_based import\
    AbstractRecordBasedRecommender
from search_rex.recommendations.recommenders.case_based import\
    AbstractQueryBasedRecommender
from search_rex.recommendations import Recommender
import mock


def test__recommender__refresh__underlying_components_are_refreshed():
    fake_q_rec = AbstractQueryBasedRecommender()
    fake_q_rec.refresh = mock.Mock()
    fake_r_rec = AbstractRecordBasedRecommender()
    fake_r_rec.refresh = mock.Mock()

    sut = Recommender(fake_r_rec, fake_q_rec)

    refreshed_components = set()
    sut.refresh(refreshed_components)

    assert fake_q_rec in refreshed_components
    assert fake_r_rec in refreshed_components
    assert sut in refreshed_components
    assert fake_q_rec.refresh.call_count == 1
    assert fake_r_rec.refresh.call_count == 1
