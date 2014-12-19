from recommender.data_model import PersistentDataModel
from recommender.data_model import InMemoryRecordBasedDataModel
import search_rex.recommender.recommenders.item_based as item_based_rec
import search_rex.recommender.recommenders.case_based as query_based_rec
import search_rex.recommender.similarity.item_based as item_based_sim
import search_rex.recommender.similarity.case_based as query_based_sim
import search_rex.recommender.neighbourhood.item_based as item_based_nhood
import search_rex.recommender.neighbourhood.case_based as query_based_nhood

from recommender.factory import create_rec_service
from models import ActionType

data_model = PersistentDataModel()
recommenders = {}


def get_recommender(action_type, include_internal_records):
    if len(recommenders) == 0:
        print("Recommenders not created")

    return recommenders[(action_type, include_internal_records)]


def create_recommender_system(app):
    print("Creating Recommender")
    def record_based_recsys_factory(action_data_model):
        in_mem_dm = InMemoryRecordBasedDataModel(action_data_model)
        sim = item_based_sim.JaccardRecordSimilarity(in_mem_dm)
        nhood = item_based_nhood.KNearestRecordNeighbourhood(
            25, in_mem_dm, sim)
        return item_based_rec.RecordBasedRecommender(
            action_data_model, nhood, sim)


    def query_based_recsys_factory(data_model):
        sim = query_based_sim.StringJaccardSimilarity(k_shingles=3)
        nhood = query_based_nhood.ThresholdQueryNeighbourhood(
            data_model, sim, sim_threshold=0.25)
        scorer = query_based_rec.WeightedScorer(
            query_based_rec.LogFrequency(base=2))
        return query_based_rec.QueryBasedRecommender(
            data_model, nhood, sim, scorer)

    with app.app_context():
        rec_pms = [
            (ActionType.copy, True),
            (ActionType.view, True),
            (ActionType.copy, False),
            (ActionType.view, False),
        ]
        for action_type, include_internal_records in rec_pms:
            print("Creating Recommender")

            rec_service = create_rec_service(
                data_model, action_type=action_type,
                include_internal_records=include_internal_records,
                record_based_recsys_factory=record_based_recsys_factory,
                query_based_recsys_factory=query_based_recsys_factory)

            recommenders[(action_type, include_internal_records)] =\
                rec_service
