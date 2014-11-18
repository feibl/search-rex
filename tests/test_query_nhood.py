from search_rex.query_nhood import ThresholdQueryNeighbourhood
from search_rex.query_sim import QuerySimilarity
from search_rex.data_model import DataModel
from mock import Mock


def test__ThresholdQueryNeighbourhood():
    query_string = 'fat cat'

    similarities = {
        'fat rat': 0.5,
        'fat fat': 0.49,
    }

    fake_model = DataModel()
    fake_sim = QuerySimilarity

    def query_sim(query1, query2):
        return similarities[query2]

    fake_sim.compute_similarity = Mock(side_effect=query_sim)
    fake_model.get_queries = Mock(return_value=similarities.keys())

    sut = ThresholdQueryNeighbourhood(
        data_model=fake_model,
        query_sim=fake_sim,
        sim_threshold=0.5)

    nbours = list(sut.get_neighbourhood(query_string))

    assert len(nbours) == 1
    assert nbours[0] == 'fat rat'
