class Recommendation(object):

    def __init__(self):
        self.record_id = None
        self.relevance_score = None
        self.comm_relevance = None
        self.related_queries = []
        self.last_interaction = None
        self.comm_popularity = None


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

    def recommend(self, query_string, n=None):
        '''Returns a list of n records that were relevant to the members of the
        community when committing the same or a similar query'''
        raise NotImplementedError()

    def register_hit(
            self, query_string, record_id, t_stamp,
            session_id):
        '''Stores a click on a search result recorded during the given
        session'''
        raise NotImplementedError()

    def get_similar_queries(self, query_string):
        '''Gets similar queries that were committed by the given community
        '''
        raise NotImplementedError()


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

    def get_similar_queries(self, query_string):
        return self.query_nhood.get_neighbourhood(query_string)

    def recommend(self, query_string, n=None):
        # TODO: Explain recommandations
        # Community: Relevance for current query
        # Related: Other queries that also led to this result
        # Time: Last time this result was selected
        # Popularity: Rank over all records
        nbours = [
            nbour for nbour, _
            in self.get_similar_queries(query_string)
        ]

        hit_rows = []
        nbour_sims = []
        records = set()

        for nbour in nbours:
            hit_row = {
                record_id: hits for record_id, hits in
                self.data_model.get_hits_for_query(nbour)
            }
            for record in hit_row.keys():
                if record not in records:
                    records.add(record)
            sim = self.query_sim.compute_similarity(
                query_string, nbour)
            hit_rows.append(hit_row)
            nbour_sims.append(sim)

        rel_scores = []
        for record in records:
            score = compute_w_relevance(record, hit_rows, nbour_sims)
            rel_scores.append((record, score))

        sorted_scores = sorted(rel_scores, key=lambda x: x[1], reverse=True)

        # Community Relevance:
        community_rel = {}
        if query_string in nbours:
            index = nbours.index(query_string)
            for record_id in hit_rows[index].keys():
                community_rel[record_id] =\
                    compute_relevance(record_id, hit_rows[index])

        # Related Queries:
        related_queries = {}
        for i, nbour in enumerate(nbours):
            if nbour == query_string:
                continue
            for record in hit_rows[i]:
                if record not in related_queries:
                    related_queries[record] = []
                related_queries[record].append(nbour)

        # Time
        last_selections = {}
        for record in records:
            last_selections[record] =\
                self.data_model.last_interaction_time(record)

        # Popularity
        popularity = {}
        for record in records:
            popularity[record] =\
                self.data_model.popularity_rank(record)

        recommendations = []
        for record, score in sorted_scores:
            recommendation = Recommendation()
            recommendation.relevance_score = score
            recommendation.record_id = record
            recommendation.comm_relevance =\
                community_rel[record] if record in community_rel else None
            recommendation.last_interaction = last_selections[record]
            recommendation.related_queries =\
                related_queries[record] if record in related_queries else []
            recommendation.comm_popularity =\
                popularity[record] if record in popularity else None
            recommendations.append(recommendation)

        return recommendations
