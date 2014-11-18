from itertools import groupby


class Recommendation(object):

    def __init__(self):
        self.record_id = None
        self.relevance_score = None
        self.comm_relevance = None
        self.related_queries = None
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
        nbours = [
            nbour for nbour
            in self.get_similar_queries(query_string)
        ]

        nbour_sims = [
            self.query_sim.compute_similarity(
                query_string, nbour) for nbour in nbours
        ]

        records = set()
        hit_rows = []
        for nbour, group in\
                groupby(
                    self.data_model.get_hits_for_queries(nbours),
                    key=lambda (nbour, record, hits): nbour):
            hit_row = {}
            for nbour, record, hits in group:
                if record not in records:
                    records.add(record)
                hit_row[record] = hits

            hit_rows.append(hit_row)

        rel_scores = []
        for record in records:
            score = compute_w_relevance(record, hit_rows, nbour_sims)
            rel_scores.append((record, score))

        sorted_scores = sorted(rel_scores, key=lambda x: x[1], reverse=True)

        # Relevance to current query:
        query_relevance = {}
        if query_string in nbours:
            index = nbours.index(query_string)
            for record_id in hit_rows[index].keys():
                query_relevance[record_id] =\
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
        last_interactions = {
            record: timestamp for record, timestamp
            in self.data_model.last_interaction_time(records)
        }

        # Popularity
        popularity = {
            record: rank for record, rank
            in self.data_model.popularity_rank(records)
        }

        recommendations = []
        for record, score in sorted_scores:
            recommendation = Recommendation()
            recommendation.relevance_score = score
            recommendation.record_id = record
            recommendation.comm_relevance =\
                query_relevance[record] if record in query_relevance else None
            recommendation.last_interaction = last_interactions[record]
            recommendation.related_queries =\
                related_queries[record] if record in related_queries else []
            recommendation.comm_popularity =\
                popularity[record] if record in popularity else None
            recommendations.append(recommendation)

        return recommendations
