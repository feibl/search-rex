from recommender.data_model import PersistentDataModel
import search_rex.recommender.recommenders.item_based as item_based_rec
import search_rex.recommender.recommenders.case_based as query_based_rec
import search_rex.recommender.similarity.item_based as item_based_sim
import search_rex.recommender.similarity.case_based as query_based_sim
import search_rex.recommender.neighbourhood.item_based as item_based_nhood
import search_rex.recommender.neighbourhood.case_based as query_based_nhood

from recommender.factory import create_rec_service
from models import ActionType

data_model = PersistentDataModel()

def record_based_recsys_factory(data_model):
    sim = item_based_sim.JaccardRecordSimilarity(data_model)
    nhood = item_based_nhood.KNearestRecordNeighbourhood(25, data_model, sim)
    return item_based_rec.RecordBasedRecommender(data_model, nhood, sim)


def query_based_recsys_factory(data_model):
    sim = query_based_sim.StringJaccardSimilarity(k_shingles=3)
    nhood = query_based_nhood.ThresholdQueryNeighbourhood(
        data_model, sim, sim_threshold=0.25)
    scorer = query_based_rec.WeightedScorer(
        query_based_rec.LogFrequency(base=2))
    return query_based_rec.QueryBasedRecommender(
        data_model, nhood, sim, scorer)

internal_copy_action_recommender = create_rec_service(
    data_model, action_type=ActionType.copy, include_internal_records=True,
    record_based_recsys_factory=record_based_recsys_factory,
    query_based_recsys_factory=query_based_recsys_factory)

internal_view_action_recommender = create_rec_service(
    data_model, action_type=ActionType.view, include_internal_records=True,
    record_based_recsys_factory=record_based_recsys_factory,
    query_based_recsys_factory=query_based_recsys_factory)

external_copy_action_recommender = create_rec_service(
    data_model, action_type=ActionType.copy, include_internal_records=False,
    record_based_recsys_factory=record_based_recsys_factory,
    query_based_recsys_factory=query_based_recsys_factory)

external_view_action_recommender = create_rec_service(
    data_model, action_type=ActionType.view, include_internal_records=False,
    record_based_recsys_factory=record_based_recsys_factory,
    query_based_recsys_factory=query_based_recsys_factory)
