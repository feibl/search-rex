from itertools import groupby


class Recommendation(object):

    def __init__(self):
        self.record_id = None
        self.relevance_score = None
        self.target_query_relevance = None
        self.related_queries = None
        self.last_interaction_time = None
        self.popularity_rank = None


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
    for query_string, nbor_hit_row in nbor_hit_rows.iteritems():
        if record_id not in nbor_hit_row:
            continue
        sim = nbor_sims[query_string]
        rel = compute_relevance(record_id, nbor_hit_row)
        total_rel += sim * rel
        total_sim += sim
    if total_sim == 0.0:
        return 0.0
    return total_rel / total_sim


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
            self, data_model, query_nhood, query_sim):
        self.data_model = data_model
        self.query_nhood = query_nhood
        self.query_sim = query_sim

    def register_hit(
            self, query_string, community_id, record_id, t_stamp,
            session_id):
        '''Stores a click on a search result recorded during the given
        session'''
        return self.data_model.register_hit(
            query_string=query_string, record_id=record_id,
            t_stamp=t_stamp, session_id=session_id)

    def get_similar_queries(self, query_string, community_id):
        return self.query_nhood.get_neighbourhood(query_string)

    def recommend(self, query_string, community_id, n=None):
        nbours = [
            nbour for nbour
            in self.get_similar_queries(query_string, community_id)
        ]

        nbour_sims = {
            nbour: self.query_sim.compute_similarity(
                query_string, nbour, community_id) for nbour in nbours
        }

        records = set()
        hit_rows = {}
        for nbour, group in\
                groupby(
                    self.data_model.get_hits_for_queries(nbours, community_id),
                    key=lambda (nbour, record, hits): nbour):
            hit_row = {}
            for nbour, record, hits in group:
                if record not in records:
                    records.add(record)
                hit_row[record] = hits

            hit_rows[nbour] = hit_row

        rel_scores = {}
        for record in records:
            score = compute_w_relevance(record, hit_rows, nbour_sims)
            rel_scores[record] = score

        rec_builder = RecommendationBuilder(
            query_string=query_string, relevance_scores=rel_scores,
            hit_rows=hit_rows, data_model=self.data_model,
            community_id=community_id)

        rec_builder.set_current_relevance()
        rec_builder.set_last_interaction_time()
        rec_builder.set_popularity_rank()
        rec_builder.set_related_queries()

        recs = rec_builder.get_recommendations()

        return sorted(
            recs.values(), key=lambda rec: rec.relevance_score, reverse=True)


class RecommendationBuilder(object):

    def __init__(
            self, query_string, relevance_scores,
            hit_rows, data_model, community_id):
        self.query_string = query_string
        self.relevance_scores = relevance_scores
        self.hit_rows = hit_rows
        self.data_model = data_model
        self.community_id = community_id

        self.recommendations = {}
        for record, score in relevance_scores.iteritems():
            rec = Recommendation()
            rec.record_id = record
            rec.relevance_score = score
            self.recommendations[record] = rec
            print((record, score))

    def set_last_interaction_time(self):
        '''Annotates every record with the timestamp of the last interaction'''
        r_iter = self.data_model.last_interaction_time(
            self.recommendations.keys(), self.community_id)

        for record, timestamp in r_iter:
            self.recommendations[record].last_interaction_time = timestamp

    def set_popularity_rank(self):
        '''Annotates every record with its popularity rank'''
        r_iter = self.data_model.popularity_rank(
            self.recommendations.keys(), self.community_id)

        for record, rank in r_iter:
            self.recommendations[record].popularity_rank = rank

    def set_related_queries(self):
        '''Annotates every record with query alternatives that also led to a
        click on the result'''
        for other_query, hit_row in self.hit_rows.iteritems():
            if other_query == self.query_string:
                continue
            for record in hit_row:
                if self.recommendations[record].related_queries is None:
                    self.recommendations[record].related_queries = []
                self.recommendations[record]\
                    .related_queries.append(other_query)

    def set_current_relevance(self):
        '''Annotates records selected by the community when entering the same
        target query with its relevance'''
        target_hit_row = self.hit_rows[self.query_string]

        for record_id in target_hit_row.keys():
            self.recommendations[record_id].target_query_relevance =\
                compute_relevance(record_id, target_hit_row)

    def get_recommendations(self):
        return self.recommendations
