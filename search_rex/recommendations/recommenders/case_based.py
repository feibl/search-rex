"""
In this module, the implementation of the case-based recommender system is
defined. The main class is the QueryBasedRecommender which is able to recommend
search results that users have found relevant after they have entered a
particular query.
"""

import math
from ..refreshable import Refreshable
from ..refreshable import RefreshHelper


class SearchResultRecommendation(object):
    """
    Recommendation object that holds informations about the recommended record
    """

    def __init__(self, record_id):
        self.record_id = record_id
        # The score calculated by the recommender
        self.score = None
        self.last_interaction = None
        self.total_hits = None

    def serialize(self):
        return {
            'record_id': self.record_id,
            'score': self.score,
            'total_hits': self.total_hits,
            'last_interaction': self.last_interaction,
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


class LogFrequency:
    """
    Calculates the log of the number of hits

    Useful for a smoothed popularity metric
    """
    def __init__(self, base=10, scale=1.0):
        self.base = base
        self.scale = scale

    def __call__(self, record_id, query_hits):
        if record_id not in query_hits:
            return 0.0
        weight = 1 + self.scale * query_hits[record_id]
        return math.log(weight, self.base) if weight > 0.0 else 0.0


class Frequency:
    """
    Returns the number of hits
    """
    def __call__(self, record_id, query_hits):
        if record_id not in query_hits:
            return 0.0
        return query_hits[record_id]


class Scorer(object):
    """
    A mathematical function that is applied on the hit-matrix entries
    """

    def compute_score(self, record_id, hit_rows, query_sims):
        raise NotImplementedError()


class WeightedSumScorer(Scorer):
    """
    Sums the scores weighted by the query similarities
    """

    def __init__(self, score_function=relevance):
        self.score_function = score_function

    def compute_score(self, record_id, hit_rows, query_sims):
        """
        Computes the score of a record including the similarities of queries to
        the target query and their hit-rows
        """
        assert len(hit_rows) == len(query_sims)
        total_score = 0.0
        for query_string, nbor_hit_row in hit_rows.iteritems():
            if record_id not in nbor_hit_row:
                continue
            sim = query_sims[query_string]
            score = self.score_function(record_id, nbor_hit_row)
            total_score += sim * score
        return total_score


class WeightedAverageScorer(Scorer):
    """
    Computes the weighted average score using the query similarities
    """

    def __init__(self, score_function=relevance):
        self.score_function = score_function

    def compute_score(self, record_id, hit_rows, query_sims):
        """
        Computes the score of a record including the similarities of queries to
        the target query and their hit-rows
        """
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


class AbstractQueryBasedRecommender(Refreshable):
    '''Recommender System for search results based on queries committed by
    members of a community'''

    def recommend_search_results(self, query_string, max_num_recs=10):
        """
        Returns a list of records that were viewed after entering the query

        :param query_string: the query that was entered by the user
        :param max_num_recs: the maximum number of recommendations to return
        """
        raise NotImplementedError()

    def get_similar_queries(self, query_string, max_num_recs=10):
        """
        Returns a list of queries which are similar to the target query

        :param query_string: the query that was entered by the user
        """
        raise NotImplementedError()


class QueryBasedRecommender(AbstractQueryBasedRecommender):

    def __init__(
            self, data_model, query_nhood, query_sim, scorer):
        self.data_model = data_model
        self.query_nhood = query_nhood
        self.query_sim = query_sim
        self.scorer = scorer
        self.refresh_helper = RefreshHelper()
        self.refresh_helper.add_dependency(data_model)
        self.refresh_helper.add_dependency(query_sim)
        self.refresh_helper.add_dependency(query_nhood)

    def get_similar_queries(self, query_string, max_num_recs=10):
        """
        Returns a list of queries which are similar to the target query

        :param query_string: the query that was entered by the user
        """
        return self.query_nhood.get_neighbours(query_string)

    def recommend_search_results(self, query_string, max_num_recs=10):
        """
        Returns a list of records that were viewed after entering the query

        :param query_string: the query that was entered by the user
        :param max_num_recs: the maximum number of recommendations to return
        """
        nbours = [
            nbour for nbour
            in self.query_nhood.get_neighbours(query_string)
        ]

        nbour_sims = {}
        for nbour in nbours:
            sim = self.query_sim.get_similarity(query_string, nbour)
            if not math.isnan(sim):
                nbour_sims[nbour] = sim

        hit_row_iter = self.data_model.get_hit_rows_for_queries(nbours)

        records = set()
        hit_rows = {}
        hit_value_rows = {}
        for nbour, hit_row in hit_row_iter:
            records.update(hit_row.keys())
            hit_rows[nbour] = hit_row
            hit_value_rows[nbour] =\
                {record: hit.value for record, hit in hit_row.items()}

        recs = {}
        for record in records:
            score = self.scorer.compute_score(
                record, hit_value_rows, nbour_sims)

            rec = SearchResultRecommendation(record)
            rec.score = score

            rec.related_queries = []
            total_hits = 0
            last_interaction = None
            for _, hit_row in hit_rows.iteritems():
                if record in hit_row:
                    record_hit = hit_row[record]

                    total_hits += record_hit.num_views
                    if last_interaction is None\
                            or record_hit.last_interaction > last_interaction:
                        last_interaction = record_hit.last_interaction

            rec.last_interaction = last_interaction
            rec.total_hits = total_hits

            recs[record] = rec

        sorted_recs = sorted(
            recs.values(), key=lambda rec: rec.score, reverse=True)

        recs_to_return = sorted_recs[:max_num_recs]
        for rec in recs_to_return:
            print('Record: {}, Score: {}'.format(
                rec.record_id, rec.score))
        return recs_to_return

    def refresh(self, refreshed_components):
        self.refresh_helper.refresh(refreshed_components)
        refreshed_components.add(self)
