import math


class QueryDetails(object):
    """
    The query Object that is returned with the recommended Record.

    It holds information about the relevance and the last interaction time
    """

    def __init__(self, query_string):
        self.query_string = query_string
        # Relevance to the target Record
        self.target_relevance = None
        # Last time the target Record was selected after this query
        self.target_last_interaction = None
        # Number of times the target Record was selected after this query
        self.total_hits = None
        # Adjusted number of hits incorporating time aspect
        self.decayed_hits = None

    def serialize(self):
        return {
            'query_string': self.query_string,
            'total_hits': self.total_hits,
            'decayed_hits': self.decayed_hits,
            'last_interaction': self.target_last_interaction,
            'relevance': self.target_relevance
        }


class Recommendation(object):

    def __init__(self, record_id):
        self.record_id = record_id
        # The score calculated by the recommender
        self.score = None
        # The committed query if available and if it generated a hit on this
        # record
        self.current_query = None
        # Related queries that generated a hit on this record
        self.related_queries = None

    def serialize(self):
        return {
            'record_id': self.record_id,
            'score': self.score,
            'current_query':
                self.current_query.serialize()
                if self.current_query else None,
            'self.related_queries':
                [
                    query.serialize() for query in self.related_queries
                ]
        }


def relevance(record_id, query_hits):
    """
    Calculates the relative number of hits on the record
    """
    if record_id not in query_hits:
        return 0.0
    total_hits = sum(hit for hit in query_hits.values())
    if total_hits == 0.0:
        return 0.0
    return float(query_hits[record_id]) / total_hits


def log_frequency(record_id, query_hits):
    """
    Returns the logarithm of the number of hits
    """
    if record_id not in query_hits or query_hits[record_id] <= 0.0:
        return 0.0
    return math.log(query_hits[record_id], 2)


class Scorer(object):

    def compute_score(self, record_id, hit_rows, query_sims):
        raise NotImplementedError()


class WeightedScorer(Scorer):
    """
    Computes the weighted average score using the query similarities
    """

    def __init__(self, score_function=relevance):
        self.score_function = score_function

    def compute_score(self, record_id, hit_rows, query_sims):
        assert len(hit_rows) == len(query_sims)
        total_score = 0.0
        total_sim = 0.0
        for query_string, nbor_hit_row in hit_rows.iteritems():
            if record_id not in nbor_hit_row:
                continue
            sim = query_sims[query_string]
            score = self.score_function(record_id, nbor_hit_row)
            total_score += sim * score
            total_sim += sim
        if total_sim == 0.0:
            return 0.0
        return total_score / total_sim


class SearchResultRecommender(object):
    '''Recommender System for search results based on queries committed by
    members of a community'''

    def recommend(self, query_string, community_id, n=None):
        '''Returns a list of n records that were relevant to the members of the
        community when committing the same or a similar query'''
        raise NotImplementedError()

    def register_hit(
            self, query_string, community_id, record_id, t_stamp,
            session_id):
        '''Stores a click on a search result recorded during the given
        session'''
        raise NotImplementedError()

    def get_similar_queries(self, query_string, community_id):
        '''Gets similar queries that were committed by the given community
        '''
        raise NotImplementedError()


class GenericSearchResultRecommender(SearchResultRecommender):

    def __init__(
            self, data_model, query_nhood, query_sim, scorer):
        self.data_model = data_model
        self.query_nhood = query_nhood
        self.query_sim = query_sim
        self.scorer = scorer

    def register_hit(
            self, query_string, community_id, record_id, t_stamp,
            session_id):
        '''Stores a click on a search result recorded during the given
        session'''
        return self.data_model.register_hit(
            query_string=query_string, community_id=community_id,
            record_id=record_id, t_stamp=t_stamp, session_id=session_id)

    def get_similar_queries(
            self, query_string, community_id, max_results=10):
        return self.query_nhood.get_neighbourhood(query_string, community_id)

    def recommend(self, query_string, community_id, max_results=10):
        nbours = [
            nbour for nbour
            in self.get_similar_queries(query_string, community_id)
        ]

        nbour_sims = {
            nbour: self.query_sim.compute_similarity(
                query_string, nbour, community_id) for nbour in nbours
        }

        hit_row_iter = self.data_model.get_hits_for_queries(
            nbours, community_id)

        records = set()
        hit_rows = {}
        hit_value_rows = {}
        for query_string, hit_row in hit_row_iter:
            records.update(hit_row.keys())
            hit_rows[query_string] = hit_row
            hit_value_rows[query_string] =\
                {record: hit.decayed_hits for record, hit in hit_row.items()}

        recs = {}
        rel_scores = {}
        for record in records:
            record_hits = []
            for q_string, hit_row in hit_rows.iteritems():
                if record in hit_row:
                    record_hits.append(hit_row[record])

            score = self.scorer.compute_score(
                record, hit_value_rows, nbour_sims)
            rel_scores[record] = score

            rec = Recommendation(record)
            rec.score = score
            rec.related_queries = []
            for record_hit in record_hits:
                q_details = QueryDetails(record_hit.query_string)
                q_details.decayed_hits = record_hit.decayed_hits
                q_details.total_hits = record_hit.total_hits
                q_details.target_last_interaction =\
                    record_hit.last_interaction

                if record_hit.query_string == query_string:
                    rec.current_query = q_details
                else:
                    rec.related_queries.append(q_details)

            recs[record] = rec

        return sorted(
            recs.values(), key=lambda rec: rec.score, reverse=True)
