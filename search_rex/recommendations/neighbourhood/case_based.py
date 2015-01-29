"""
In this module, the classes for forming the queries' neighbourhoods are
implemented. The main class in this module is the QueryNeighbourhood. For a
target query, this class searches for past queries that are similar to the
target one. This is achieved by using a class for calculating the similarity of
two queries.
"""

from ..refreshable import Refreshable
from ..refreshable import RefreshHelper


class AbstractQueryNeighbourhood(Refreshable):
    """
    Retrieves the neighbours of a particular query
    """

    def get_neighbours(self, query_string):
        '''Retrieves a list of queries that belong to the neighbourhood of
        the given query'''
        raise NotImplementedError()


class ThresholdQueryNeighbourhood(AbstractQueryNeighbourhood):
    """
    The neighbourhood of a query consists of queries that is equals or
    greater than a specified similarity threshold. The latter is calculated by
    a given query similarity metric
    """

    def __init__(self, data_model, query_sim, sim_threshold):
        self.data_model = data_model
        self.query_sim = query_sim
        self.sim_threshold = sim_threshold
        self.refresh_helper = RefreshHelper()
        self.refresh_helper.add_dependency(data_model)
        self.refresh_helper.add_dependency(query_sim)

    def get_neighbours(self, query_string):
        """
        Returns the queries whose similarity to the target query is higher than
        the specified threshold
        """
        for other_q_string in self.data_model.get_queries():
            similarity = self.query_sim.get_similarity(
                query_string, other_q_string)

            if similarity >= self.sim_threshold:
                yield other_q_string

    def refresh(self, refreshed_components):
        self.refresh_helper.refresh(refreshed_components)
        refreshed_components.add(self)
