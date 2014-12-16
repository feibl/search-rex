from search_rec import GenericRecommender
from search_rec import WeightedSumScorer
from search_rec import LogFrequency
from query_sim import StringJaccardSimilarity
from query_nhood import ThresholdQueryNeighbourhood
from data_model import PersistentDataModel
from models import ActionType


def create_rec_system(k_shingles=3, sim_threshold=0.2):
    d_model = PersistentDataModel(
        action_type=ActionType.copy, include_internal_records=False)
    q_sim = StringJaccardSimilarity(k_shingles=k_shingles)
    q_nhood = ThresholdQueryNeighbourhood(
        data_model=d_model, query_sim=q_sim, sim_threshold=sim_threshold)
    return GenericRecommender(
        data_model=d_model,
        query_sim=q_sim,
        query_nhood=q_nhood,
        scorer=WeightedSumScorer(LogFrequency()))
