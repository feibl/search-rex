from search_rex.recommendations.neighbourhood.case_based import\
    ThresholdQueryNeighbourhood
from search_rex.recommendations.similarity.case_based import\
    AbstractQuerySimilarity
from search_rex.recommendations.data_model.case_based import\
    AbstractQueryDataModel
import mock


def test__ThresholdQueryNeighbourhood():
    query_string = 'fat cat'

    similarities = {
        'fat rat': 0.5,
        'fat fat': 0.49,
    }

    fake_model = AbstractQueryDataModel()
    fake_sim = AbstractQuerySimilarity()

    def query_sim(query1, query2):
        return similarities[query2]

    def get_queries():
        return similarities.keys()

    fake_sim.get_similarity = mock.Mock(side_effect=query_sim)
    fake_model.get_queries = mock.Mock(side_effect=get_queries)

    sut = ThresholdQueryNeighbourhood(
        data_model=fake_model,
        query_sim=fake_sim,
        sim_threshold=0.5)

    nbours = list(sut.get_neighbours(query_string))

    assert len(nbours) == 1
    assert nbours[0] == 'fat rat'


def test__thres_nhood__refresh__data_model_and_similarity_refreshed():
    fake_model = AbstractQueryDataModel()
    fake_model.refresh = mock.Mock()
    fake_sim = AbstractQuerySimilarity()
    fake_sim.refresh = mock.Mock()

    sut = ThresholdQueryNeighbourhood(
        data_model=fake_model,
        query_sim=fake_sim,
        sim_threshold=0.5)

    refreshed_components = set()
    sut.refresh(refreshed_components)

    assert fake_model in refreshed_components
    assert fake_sim in refreshed_components
    assert sut in refreshed_components
    assert fake_model.refresh.call_count == 1
    assert fake_sim.refresh.call_count == 1
