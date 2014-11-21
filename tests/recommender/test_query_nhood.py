from search_rex.recommender.query_nhood import ThresholdQueryNeighbourhood
from search_rex.recommender.query_sim import QuerySimilarity
from search_rex.recommender.data_model import DataModel
from mock import Mock


def test__ThresholdQueryNeighbourhood():
    query_string = 'fat cat'
    community_id = 'freaks'

    similarities = {
        'fat rat': 0.5,
        'fat fat': 0.49,
    }

    fake_model = DataModel()
    fake_sim = QuerySimilarity

    def query_sim(query1, query2, community_id):
        return similarities[query2]

    def get_queries(community_id):
        return similarities.keys()

    fake_sim.compute_similarity = Mock(side_effect=query_sim)
    fake_model.get_queries = Mock(side_effect=get_queries)

    sut = ThresholdQueryNeighbourhood(
        data_model=fake_model,
        query_sim=fake_sim,
        sim_threshold=0.5)

    nbours = list(sut.get_neighbourhood(query_string, community_id))

    assert len(nbours) == 1
    assert nbours[0] == 'fat rat'
