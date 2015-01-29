"""
This module is the main entry point for accessing the recommendation services.
It provides a factory method that is called for creating the two recommender
instances. One of these instances is used for internal users who are allowed
to see HSR-internal documents. The other instance is applied when HSR-internal
documents should not be recommended. This is the case for external users.
Further, this module also holds these recommender instances once they are
created. For this reason, it is accessed by the search_rex.views module in
order to generate recommendations for the users.
"""

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


recommender_instances = {}


def get_recommender(include_internal_records):
    """
    Returns either the internal or the external recommender instance
    """
    if len(recommender_instances) == 0:
        print("Recommenders not created")

    return recommender_instances[include_internal_records]


def refresh_recommenders():
    """
    Refreshes the components of the recommenders
    """
    for recommender in recommender_instances.values():
        refreshed_components = set()
        recommender.refresh(refreshed_components)


def create_recommender_system(
        app,
        record_based_recsys_factory=None,
        query_based_recsys_factory=None):
    """
    The factory method for creating the recommender instances

    :param app: the flask app
    :param record_based_recsys_factory: optional factory method for creating
    the record-based recommender
    :param query_based_recsys_factory: optional factory method for creating
    the query-based recommender
    """
    print("Creating Recommender")

    def r_based_recsys_factory(include_internal_records):
        data_model = item_based_dm.PersistentRecordDataModel(
            include_internal_records)

        in_mem_dm = item_based_dm.InMemoryRecordDataModel(data_model)
        content_sim = item_based_sim.InMemoryRecordSimilarity(
            include_internal_records)
        sim_metric = item_based_sim.CosineSimilarity()
        sim_metric = item_based_sim.TimeDecaySimilarity(sim_metric)
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
        scorer = query_based_rec.WeightedSumScorer(
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

            recommender_instances[include_internal_records] =\
                rec_service


class Recommender(Refreshable):
    """
    The recommender instance that consists of a record-based and a query-based
    recommender
    """

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
        """
        Returns a list of queries which are similar to the target query

        :param query_string: the query that was entered by the user
        """
        return self.query_based_recsys.get_similar_queries(
            query_string, max_num_recs)

    def recommend_search_results(self, query_string, max_num_recs=10):
        """
        Returns a list of records that were viewed after entering the query

        :param query_string: the query that was entered by the user
        :param max_num_recs: the maximum number of recommendations to return
        """
        return self.query_based_recsys.recommend_search_results(
            query_string, max_num_recs)

    def other_users_also_used(self, record_id, max_num_recs=10):
        """
        Returns a list of records that were used together with the given one

        :param session_id: the id of the record
        :param max_num_recs: the maximum number of recommendations to return
        """
        return self.record_based_recsys.most_similar_records(
            record_id, max_num_recs)

    def influenced_by_your_history(self, session_id, max_num_recs=10):
        """
        Gets a list of recommended records based on a session's history

        :param session_id: the id of the session to which the records are
        recommended
        :param max_num_recs: the maximum number of recommendations to return
        """
        return self.record_based_recsys.recommend(
            session_id, max_num_recs)

    def refresh(self, refreshed_components):
        self.refresh_helper.refresh(refreshed_components)
        refreshed_components.add(self)
