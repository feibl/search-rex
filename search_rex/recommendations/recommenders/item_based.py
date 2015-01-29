"""
In this module, the implementation of the item-based recommender system is
defined. The main class is the RecordBasedRecommender which is able to
recommend geodata records by learning the users' interests.
"""

from collections import defaultdict
from ..refreshable import Refreshable
from ..refreshable import RefreshHelper
import math
import logging


logger = logging.getLogger(__name__)


class AbstractRecordBasedRecommender(Refreshable):
    """
    An item-based recommender system for recommending records to the users by
    incorporating their history of views and copies
    """

    def recommend(self, session_id, max_num_recs=10):
        """
        Gets a list of recommended records based on a session's history

        :param session_id: the id of the session to which the records are
        recommended
        :param max_num_recs: the maximum number of recommendations to return
        """

        raise NotImplementedError()

    def most_similar_records(self, record_id, max_num_recs=10):
        """
        Returns a list of records that were used together with the given one

        :param session_id: the id of the record
        :param max_num_recs: the maximum number of recommendations to return
        """
        raise NotImplementedError()


class RecordBasedRecommender(AbstractRecordBasedRecommender):
    """
    An item-based recommender system for recommending records to the users by
    incorporating their history of views and copies
    """

    def __init__(self, data_model, record_nhood, record_sim):
        self.data_model = data_model
        self.record_nhood = record_nhood
        self.record_sim = record_sim
        self.refresh_helper = RefreshHelper()
        self.refresh_helper.add_dependency(data_model)
        self.refresh_helper.add_dependency(record_sim)
        self.refresh_helper.add_dependency(record_nhood)

    def recommend(self, session_id, max_num_recs=10):
        """
        Gets a list of recommended records based on a session's history

        :param session_id: the id of the session to which the records are
        recommended
        :param max_num_recs: the maximum number of recommendations to return
        """
        candidates = defaultdict(float)
        preferences = self.data_model.get_preferences_of_session(session_id)
        print('Seen records by {}: {}'.format(session_id, preferences))
        for record, _ in preferences.iteritems():
            for nbour in self.record_nhood.get_neighbours(record):
                if nbour in preferences:
                    continue

                similarity = self.record_sim.get_similarity(
                    record, nbour)
                if not math.isnan(similarity):
                    candidates[nbour] += similarity

        candidates_by_score = sorted(
            candidates.items(), key=lambda (p_id, sim): sim,
            reverse=True)

        return candidates_by_score[:max_num_recs]\
            if max_num_recs is not None else candidates_by_score

    def most_similar_records(self, record_id, max_num_recs=10):
        """
        Returns a list of records that were used together with the given one

        :param session_id: the id of the record
        :param max_num_recs: the maximum number of recommendations to return
        """
        candidates = []
        for nbour in self.record_nhood.get_neighbours(record_id):
            similarity = self.record_sim.get_similarity(record_id, nbour)
            if not math.isnan(similarity):
                candidates.append((nbour, similarity))

        candidates_by_score = sorted(
            candidates, key=lambda (p_id, sim): sim,
            reverse=True)

        return candidates_by_score[:max_num_recs]\
            if max_num_recs is not None else candidates_by_score

    def refresh(self, refreshed_components):
        self.refresh_helper.refresh(refreshed_components)
        refreshed_components.add(self)
