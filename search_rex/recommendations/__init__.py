import data_model.item_based as item_based_dm
import data_model.case_based as case_based_dm
import recommenders.item_based as item_based_rec
import recommenders.case_based as query_based_rec
import similarity.item_based as item_based_sim
import similarity.case_based as query_based_sim
import neighbourhood.item_based as item_based_nhood
import neighbourhood.case_based as query_based_nhood

from ..models import ActionType


recommenders = {}


def get_recommender(action_type, include_internal_records):
    if len(recommenders) == 0:
        print("Recommenders not created")

    return recommenders[(action_type, include_internal_records)]


def create_recommender_system(app):
    print("Creating Recommender")

    def record_based_recsys_factory(action_type, include_internal_records):
        data_model = item_based_dm.RecordBasedDataModel(
            action_type, include_internal_records)

        in_mem_dm = item_based_dm.InMemoryRecordBasedDataModel(data_model)
        sim = item_based_sim.JaccardRecordSimilarity(in_mem_dm)
        nhood = item_based_nhood.KNearestRecordNeighbourhood(
            25, in_mem_dm, sim)

        return item_based_rec.RecordBasedRecommender(data_model, nhood, sim)


    def query_based_recsys_factory(action_type, include_internal_records):
        data_model = case_based_dm.QueryBasedDataModel(
            action_type, include_internal_records)

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
            q_based_recsys = query_based_recsys_factory(
                action_type, include_internal_records)
            r_based_recsys = record_based_recsys_factory(
                action_type, include_internal_records)

            rec_service = Recommender(
                query_based_recsys=q_based_recsys,
                record_based_recsys=r_based_recsys)

            recommenders[(action_type, include_internal_records)] =\
                    rec_service


class Recommender():

    def __init__(
            self, record_based_recsys, query_based_recsys):
        self.record_based_recsys = record_based_recsys
        self.query_based_recsys = query_based_recsys

    def get_similar_queries(self, query_string, max_num_recs=10):
        return self.query_based_recsys.get_similar_queries(
            query_string, max_num_recs)

    def recommend_search_results(self, query_string, max_num_recs=10):
        return self.query_based_recsys.recommend_search_results(
            query_string, max_num_recs)

    def get_similar_records(self, record_id, max_num_recs=10):
        return self.record_based_recsys.get_similar_records(
            record_id, max_num_recs)

    def recommend_from_history(self, session_id, max_num_recs=10):
        return self.record_based_recsys.recommend(
            session_id, max_num_recs)
