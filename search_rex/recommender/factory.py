from search_rec import GenericSearchResultRecommender
from search_rec import WeightedScorer
from search_rec import LogFrequency
from query_sim import StringJaccardSimilarity
from query_nhood import ThresholdQueryNeighbourhood
from data_model import PersistentDataModel


def create_rec_system(k_shingles=3, sim_threshold=0.2):
    d_model = PersistentDataModel()
    q_sim = StringJaccardSimilarity(k_shingles=k_shingles)
    q_nhood = ThresholdQueryNeighbourhood(
        data_model=d_model, query_sim=q_sim, sim_threshold=sim_threshold)
    return GenericSearchResultRecommender(
        data_model=d_model,
        query_sim=q_sim,
        query_nhood=q_nhood,
        scorer=WeightedScorer(LogFrequency()))
