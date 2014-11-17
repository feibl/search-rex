def compute_relevance(record_id, query_hits):
    if record_id not in query_hits:
        return 0.0
    total_hits = sum(hit for hit in query_hits.values())
    return float(query_hits[record_id]) / total_hits


def compute_w_relevance(record_id, nbor_hit_rows, nbor_sims):
    '''Computes the weighted relevance of a document'''
    assert len(nbor_hit_rows) == len(nbor_sims)

    total_rel = 0.0
    total_sim = 0.0
    for i, nbor_hit_row in enumerate(nbor_hit_rows):
        if record_id not in nbor_hit_row:
            continue
        sim = nbor_sims[i]
        rel = compute_relevance(record_id, nbor_hit_row)
        total_rel += sim * rel
        total_sim += sim
    if total_sim == 0.0:
        return 0.0
    return total_rel / total_sim


class SearchResultRecommender(object):
    '''Recommender System for search results based on queries committed by
    members of a community'''

    def recommend(query_string, n=None):
        '''Returns a list of n records that were relevant to the members of the
        community when committing the same or a similar query'''
        pass

    def register_hit(
            query_string, record_id, t_stamp,
            session_id):
        '''Stores a click on a search result recorded during the given
        session'''
        pass

    def get_similar_queries(query_string, community_id=None):
        '''Gets similar queries that were committed by the given community
        '''
        pass


class GenericSearchResultRecommender(SearchResultRecommender):

    def __init__(
            self, data_model, query_nhood, query_sim):
        self.data_model = data_model
        self.query_nhood = query_nhood
        self.query_sim = query_sim

    def register_hit(
            self, query_string, record_id, t_stamp,
            session_id):
        '''Stores a click on a search result recorded during the given
        session'''
        return self.data_model.register_hit(
            query_string=query_string, record_id=record_id,
            t_stamp=t_stamp, session_id=session_id)
