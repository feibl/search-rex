import math


class AbstractRecordNeighbourhood(object):
    """
    Retrieves the neighbours of a record
    """

    def get_neighbours(self, record_id):
        raise NotImplementedError()


class KNearestRecordNeighbourhood(object):
    """
    Retrieves k records that are most similar to the given record
    """

    def __init__(self, k, data_model, record_sim):
        self.k = k
        self.data_model = data_model
        self.record_sim = record_sim

    def get_neighbours(self, record_id):
        candidates = {}
        for other_record in self.data_model.get_records():
            similarity = self.record_sim.get_similarity(
                record_id, other_record)
            if math.isnan(similarity):
                continue
            if other_record == record_id:
                continue
            candidates[other_record] = similarity

        candidates_by_score = sorted(
            candidates.iteritems(), key=lambda (r_id, sim): sim,
            reverse=True)[:self.k]

        return [r_id for r_id, sim in candidates_by_score]
