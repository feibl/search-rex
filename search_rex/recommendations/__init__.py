from .refreshable import Refreshable
from .refreshable import RefreshHelper
import data_model.item_based as item_based_dm
import data_model.case_based as case_based_dm
import recommenders.item_based as item_based_rec
import recommenders.case_based as query_based_rec
import similarity.item_based as item_based_sim
import similarity.case_based as query_based_sim
import neighbourhood.item_based as item_based_nhood
import neighbourhood.case_based as query_based_nhood


recommenders = {}


def get_recommender(include_internal_records):
    if len(recommenders) == 0:
        print("Recommenders not created")

    return recommenders[include_internal_records]


def refresh_recommenders():
    for recommender in recommenders.values():
        refreshed_components = set()
        recommender.refresh(refreshed_components)


def create_recommender_system(
        app,
        record_based_recsys_factory=None,
        query_based_recsys_factory=None):
    print("Creating Recommender")

    def r_based_recsys_factory(include_internal_records):
        data_model = item_based_dm.PersistentRecordDataModel(
            include_internal_records)

        in_mem_dm = item_based_dm.InMemoryRecordDataModel(data_model)
        content_sim = item_based_sim.InMemoryRecordSimilarity(
            include_internal_records)
        sim_metric = item_based_sim.CosineSimilarity()
        collaborative_sim = item_based_sim.RecordSimilarity(
            in_mem_dm, sim_metric)
        combined_sim = item_based_sim.CombinedRecordSimilarity(
            collaborative_sim, content_sim, weight=0.75)

        nhood = item_based_nhood.KNearestRecordNeighbourhood(
            10, in_mem_dm, combined_sim)

        return item_based_rec.RecordBasedRecommender(
            data_model, record_nhood=nhood, record_sim=combined_sim)

    def q_based_recsys_factory(include_internal_records):
        data_model = case_based_dm.PersistentQueryDataModel(
            include_internal_records)

        in_mem_dm = case_based_dm.InMemoryQueryDataModel(data_model)
        sim = query_based_sim.StringJaccardSimilarity(k_shingles=3)
        nhood = query_based_nhood.ThresholdQueryNeighbourhood(
            in_mem_dm, sim, sim_threshold=0.25)
        scorer = query_based_rec.WeightedScorer(
            query_based_rec.LogFrequency(base=2))

        return query_based_rec.QueryBasedRecommender(
            in_mem_dm, nhood, sim, scorer)

    record_based_recsys_factory = record_based_recsys_factory\
        if record_based_recsys_factory else r_based_recsys_factory

    query_based_recsys_factory = query_based_recsys_factory\
        if query_based_recsys_factory else q_based_recsys_factory

    with app.app_context():
        rec_pms = [
            True,
            False,
        ]
        for include_internal_records in rec_pms:
            q_based_recsys = query_based_recsys_factory(
                include_internal_records)
            r_based_recsys = record_based_recsys_factory(
                include_internal_records)

            rec_service = Recommender(
                query_based_recsys=q_based_recsys,
                record_based_recsys=r_based_recsys)

            recommenders[include_internal_records] =\
                rec_service


class Recommender(Refreshable):

    def __init__(
            self, record_based_recsys, query_based_recsys):
        self.record_based_recsys = record_based_recsys
        self.query_based_recsys = query_based_recsys
        self.refresh_helper = RefreshHelper()
        self.refresh_helper.add_dependency(
            record_based_recsys)
        self.refresh_helper.add_dependency(
            query_based_recsys)

    def get_similar_queries(self, query_string, max_num_recs=10):
        return self.query_based_recsys.get_similar_queries(
            query_string, max_num_recs)

    def recommend_search_results(self, query_string, max_num_recs=10):
        return self.query_based_recsys.recommend_search_results(
            query_string, max_num_recs)

    def other_users_also_used(self, record_id, max_num_recs=10):
        return self.record_based_recsys.most_similar_records(
            record_id, max_num_recs)

    def influenced_by_your_history(self, session_id, max_num_recs=10):
        return self.record_based_recsys.recommend(
            session_id, max_num_recs)

    def refresh(self, refreshed_components):
        self.refresh_helper.refresh(refreshed_components)
        refreshed_components.add(self)
