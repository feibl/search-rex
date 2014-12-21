class AbstractQueryNeighbourhood(object):
    '''Computes the neighbourhood of a target query'''

    def get_neighbours(self, query_string):
        '''Retrieves a list of queries that belong to the neighbourhood of
        the given query'''
        raise NotImplementedError()


class ThresholdQueryNeighbourhood(AbstractQueryNeighbourhood):
    '''The neighbourhood of a query consists of queries that is equals or
    greater than a specified similarity threshold. The latter is calculated by
    a given query similarity metric'''

    def __init__(self, data_model, query_sim, sim_threshold):
        self.data_model = data_model
        self.query_sim = query_sim
        self.sim_threshold = sim_threshold

    def get_neighbours(self, query_string):
        for other_q_string in self.data_model.get_queries():
            similarity = self.query_sim.get_similarity(
                query_string, other_q_string)

            if similarity >= self.sim_threshold:
                yield other_q_string
