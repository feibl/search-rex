from search_rex.recommendations.neighbourhood.case_based import\
    ThresholdQueryNeighbourhood
from search_rex.recommendations.similarity.case_based import\
    AbstractQuerySimilarity
from search_rex.recommendations.data_model.case_based import\
    AbstractQueryBasedDataModel
from mock import Mock


def test__ThresholdQueryNeighbourhood():
    query_string = 'fat cat'

    similarities = {
        'fat rat': 0.5,
        'fat fat': 0.49,
    }

    fake_model = AbstractQueryBasedDataModel()
    fake_sim = AbstractQuerySimilarity()

    def query_sim(query1, query2):
        return similarities[query2]

    def get_queries():
        return similarities.keys()

    fake_sim.get_similarity = Mock(side_effect=query_sim)
    fake_model.get_queries = Mock(side_effect=get_queries)

    sut = ThresholdQueryNeighbourhood(
        data_model=fake_model,
        query_sim=fake_sim,
        sim_threshold=0.5)

    nbours = list(sut.get_neighbours(query_string))

    assert len(nbours) == 1
    assert nbours[0] == 'fat rat'
