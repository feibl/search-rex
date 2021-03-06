"""
In this module, the classes for forming the records' neighbourhoods are
implemented. The main class in this module is the InMemoryRecordNeighbourhood.
This class calculates the neighbourhood of each record and stores it in the
local memory.
"""

from ..similarity.item_based import AbstractRecordSimilarity
from ..refreshable import Refreshable
from ..refreshable import RefreshHelper
import math


class AbstractRecordNeighbourhood(Refreshable):
    """
    Retrieves the neighbours of a record
    """

    def get_neighbours(self, record_id):
        raise NotImplementedError()


class KNearestRecordNeighbourhood(AbstractRecordNeighbourhood):
    """
    Retrieves k records that are most similar to the given record
    """

    def __init__(self, k, data_model, record_sim):
        """
        :param k: the number of records that belong to the neighbourhood of a
        target record
        :param data_model: the data model from which the records are retrieved
        :param record_sim: the object for calculating the record similarities
        """
        self.k = k
        self.data_model = data_model
        self.record_sim = record_sim
        self.refresh_helper = RefreshHelper()
        self.refresh_helper.add_dependency(data_model)
        self.refresh_helper.add_dependency(record_sim)

    def get_neighbours(self, record_id):
        """
        Retrieves k records that are most similar to the given record
        """
        candidates = {}
        for other_record in self.data_model.get_records():
            similarity = self.record_sim.get_similarity(
                record_id, other_record)
            if math.isnan(similarity):
                continue
            if similarity == 0.0:
                continue
            if other_record == record_id:
                continue
            candidates[other_record] = similarity

        candidates_by_score = sorted(
            candidates.iteritems(), key=lambda (r_id, sim): sim,
            reverse=True)[:self.k]

        return [r_id for r_id, sim in candidates_by_score]

    def refresh(self, refreshed_components):
        self.refresh_helper.refresh(refreshed_components)
        refreshed_components.add(self)


class InMemoryRecordNeighbourhood(
        AbstractRecordNeighbourhood, AbstractRecordSimilarity):
    """
    Stores for each record the a maximum number of nearest neighbours
    """

    def __init__(
            self, data_model, record_sim, max_num_nbours=100,
            nhood_factory=lambda dm, sim, num_nh:
            KNearestRecordNeighbourhood(num_nh, dm, sim)):
        """
        :param data_model: the data model from which the records are retrieved
        :param record_sim: the object for calculating the record similarities
        :param max_sims_per_record: the maximum numbers of similarities to be
        stored per record
        :param nhood_factory: factory method for creating the neighbourhood
        object
        """
        self.data_model = data_model
        self.record_sim = record_sim
        self.nhood_factory = nhood_factory
        self.max_num_nbours = max_num_nbours

        self.nbours_dict = {}

        self.refresh_helper = RefreshHelper(
            target_refresh_function=self.init_similarities)
        self.refresh_helper.add_dependency(data_model)
        self.refresh_helper.add_dependency(record_sim)

        self.init_similarities()

    def init_similarities(self):
        record_nhood = self.nhood_factory(
            self.data_model, self.record_sim, self.max_num_nbours)
        nbours_dict = {}
        for i, record in enumerate(self.data_model.get_records()):
            nbours = record_nhood.get_neighbours(record)
            nbours_dict[record] = {
                nbour: self.record_sim.get_similarity(record, nbour)
                for nbour in nbours
            }
            if i % 100 == 0:
                print(i)
        self.nbours_dict = nbours_dict

    def get_neighbours(self, record_id):
        if record_id in self.nbours_dict:
            return self.nbours_dict[record_id].keys()
        return []

    def get_similarity(self, from_record_id, to_record_id):
        if from_record_id in self.nbours_dict:
            if to_record_id in self.nbours_dict[from_record_id]:
                return self.nbours_dict[from_record_id][to_record_id]
        return float('nan')

    def refresh(self, refreshed_components):
        self.refresh_helper.refresh(refreshed_components)
        refreshed_components.add(self)
