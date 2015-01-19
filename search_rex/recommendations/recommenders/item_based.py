from collections import defaultdict
import math
import logging


logger = logging.getLogger(__name__)


class AbstractRecordBasedRecommender(object):
    """
    An item-based recommender system for recommending records to the user
    """

    def recommend(self, session_id, max_num_recs=10):
        """
        Recommends records based on the recent actions in the session
        """
        raise NotImplementedError()

    def most_similar_records(self, record_id, max_num_recs=10):
        """
        Retrieves the records most similar to the given one
        """
        raise NotImplementedError()


class RecordBasedRecommender(AbstractRecordBasedRecommender):
    """
    An item-based recommender system for recommending records to the user
    """

    def __init__(self, data_model, record_nhood, record_sim):
        self.data_model = data_model
        self.record_nhood = record_nhood
        self.record_sim = record_sim

    def recommend(self, session_id, max_num_recs=10):
        """
        Recommends records based on the recent actions in the session
        """
        candidates = defaultdict(float)
        seen_records = list(self.data_model.get_seen_records(session_id))
        print('Seen records by {}: {}'.format(session_id, seen_records))
        for seen_record in seen_records:
            for nbour in self.record_nhood.get_neighbours(seen_record):
                if nbour in seen_records:
                    continue

                similarity = self.record_sim.get_similarity(
                    seen_record, nbour)
                if not math.isnan(similarity):
                    candidates[nbour] += similarity

        candidates_by_score = sorted(
            candidates.items(), key=lambda (p_id, sim): sim,
            reverse=True)

        return candidates_by_score[:max_num_recs]\
            if max_num_recs is not None else candidates_by_score

    def most_similar_records(self, record_id, max_num_recs=10):
        """
        Retrieves records that are most similar to the given record
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
