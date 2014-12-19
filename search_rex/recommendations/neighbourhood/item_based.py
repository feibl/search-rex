from ..similarity.item_based import AbstractRecordSimilarity
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


class InMemoryKNearestRecordNeighbourhood(
        AbstractRecordNeighbourhood, AbstractRecordSimilarity):
    """
    Stores for each record the k nearest neighbours
    """

    def __init__(self, k, data_model, record_sim):
        self.k = k
        self.data_model = data_model
        self.record_sim = record_sim
        self.init_similarities()

    def init_similarities(self):
        nbours_dict = {}
        for record in self.data_model.get_records():
            nbours = self.__get_neighbours(record)
            nbours_dict[record] = {
                nbour: sim for nbour, sim in nbours
            }
        self.nbours_dict = nbours_dict

    def get_neighbours(self, record_id):
        if record_id in self.nbours_dict:
            return self.nbours_dict[record_id]
        return []

    def get_similarity(self, from_record_id, to_record_id):
        if from_record_id in self.nbours_dict:
            if to_record_id in self.nbours_dict[from_record_id]:
                return self.nbours_dict[from_record_id][to_record_id]
        return float('nan')

    def __get_neighbours(self, record_id):
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

        return candidates_by_score
