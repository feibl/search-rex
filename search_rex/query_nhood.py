class QueryNeighbourhood(object):
    '''Computes the neighbourhood of a target query'''

    def get_neighbourhood(query_string):
        '''Retrieves a list of queries that belong to the neighbourhood of
        the given query'''
        raise NotImplementedError()


class ThresholdQueryNeighbourhood(object):
    '''The neighbourhood of a query consists of queries that is equals or
    greater than a specified similarity threshold. The latter is calculated by
    a given query similarity metric'''

    def __init__(self, data_model, query_sim, sim_threshold):
        self.data_model = data_model
        self.query_sim = query_sim
        self.sim_threshold = sim_threshold

    def get_neighbourhood(self, query_string):
        neighbours = []
        for other_q_string in self.data_model.get_queries():
            similarity = self.query_sim.compute_similarity(
                query_string, other_q_string)

            print('{}: {}'.format(other_q_string, similarity))

            if similarity >= self.sim_threshold:
                neighbours.append((other_q_string, similarity))

        return neighbours
