"""
In this module, the similarity classes of the item-based approach are defined.
The most important classes are the CombinedRecordSimilarity, the
CollaborativeRecordSimilarity and the ContentRecordSimilarity. The first one
combines the record similarity values of two underlying item based similarity
classes. The second similarity class calculates the similarity of two records
by using a similarity metric, e.g., cosine similarity, on their preference
vectors. Finally, ContentRecordSimilarity retrieves the imported content-based
similarity from the database and stores in the local memory.
"""

from similarity_metrics import jaccard_sim
from similarity_metrics import cosine_sim
from .. import queries
from ..refreshable import Refreshable
from ..refreshable import RefreshHelper
from search_rex.util.date_util import utcnow
import math
from datetime import timedelta
from collections import defaultdict


class AbstractRecordSimilarity(Refreshable):
    """
    Computes the similarity from one record to the other
    """

    def get_similarity(self, from_record_id, to_record_id):
        """
        Computes the similarity from one record to the other
        """
        raise NotImplementedError()


class RecordSimilarity(AbstractRecordSimilarity):
    """
    Computes the similarity from one record to the other by comparing their
    preferences using a similarity metric
    """

    def __init__(self, data_model, similarity_metric):
        """
        :param data_model: the data model where the preferences are stored
        :param similarity_metric: the metric that computes the similarity
        between the preference vectors
        """
        self.data_model = data_model
        self.similarity_metric = similarity_metric
        self.refresh_helper = RefreshHelper()
        self.refresh_helper.add_dependency(data_model)

    def get_similarity(self, from_record_id, to_record_id):
        """
        Computes the similarity from one record to the other by comparing their
        preferences using a similarity metric
        :param from_record_id: the id of the record from which the similarity
        is directed
        :param from_record_id: the id of the record to which the similarity
        is directed
        """

        from_preferences = self.data_model.get_preferences_for_record(
            from_record_id)
        to_preferences = self.data_model.get_preferences_for_record(
            to_record_id)
        return self.similarity_metric.get_similarity(
            from_preferences, to_preferences)

    def refresh(self, refreshed_components):
        self.refresh_helper.refresh(refreshed_components)
        refreshed_components.add(self)


class CombinedRecordSimilarity(AbstractRecordSimilarity):
    """
    Combines the similarity value of two similarity metrics by applying a
    weight on each similarities

    sim = w * sim1 + (1-w) * sim2
    """

    def __init__(self, similarity_metric1, similarity_metric2, weight):
        """
        :param similarity_metric1: the first similarity metric
        :param similarity_metric2: the second similarity metric
        :param weight: the weight between 0 and 1 of metric 1
        """
        assert weight >= 0 and weight <= 1
        self.similarity_metric1 = similarity_metric1
        self.similarity_metric2 = similarity_metric2
        self.weight = weight
        self.refresh_helper = RefreshHelper()
        self.refresh_helper.add_dependency(similarity_metric1)
        self.refresh_helper.add_dependency(similarity_metric2)

    def get_similarity(self, from_record_id, to_record_id):
        """
        Computes the similarity from one record to the other by comparing their
        preferences using a similarity metric

        :param from_record_id: the id of the record from which the similarity
        is directed
        :param from_record_id: the id of the record to which the similarity
        is directed
        """
        sim1 = self.similarity_metric1.get_similarity(
            from_record_id, to_record_id)
        sim2 = self.similarity_metric2.get_similarity(
            from_record_id, to_record_id)

        if math.isnan(sim1):
            return sim2 * (1-self.weight)
        if math.isnan(sim2):
            return sim1 * self.weight
        return sim1 * self.weight + sim2 * (1-self.weight)

    def refresh(self, refreshed_components):
        self.refresh_helper.refresh(refreshed_components)
        refreshed_components.add(self)


class InMemoryRecordSimilarity(AbstractRecordSimilarity):
    """
    Loads similarities from the database and stores them in the memory
    """
    def __init__(self, include_internal_records, max_sims_per_record=100):
        self.include_internal_records = include_internal_records
        self.max_sims_per_record = max_sims_per_record
        self.similarities = {}
        self.refresh_helper = RefreshHelper(
            target_refresh_function=self.init_similarities)
        self.init_similarities()

    def init_similarities(self):
        similarities = defaultdict(dict)
        for from_record, rec_sims in queries.get_similarities(
                self.include_internal_records):
            sorted_sims = sorted(
                rec_sims.iteritems(), key=lambda(_, s): s, reverse=True)
            for i, (to_record, sim) in enumerate(sorted_sims):
                if i >= self.max_sims_per_record:
                    break
                similarities[from_record][to_record] = sim
        self.similarities = similarities

    def get_similarity(self, from_record_id, to_record_id):
        """
        Computes the similarity from one record to the other by comparing their
        preferences using a similarity metric

        :param from_record_id: the id of the record from which the similarity
        is directed
        :param from_record_id: the id of the record to which the similarity
        is directed
        """
        if from_record_id in self.similarities:
            if to_record_id in self.similarities[from_record_id]:
                return self.similarities[from_record_id][to_record_id]
        return float('nan')

    def refresh(self, refreshed_components):
        self.refresh_helper.refresh(refreshed_components)
        refreshed_components.add(self)


class AbstractPreferenceSimilarity(object):
    """
    Computes the similarity from one preference vector to the other
    """

    def get_similarity(self, from_preferences, to_preferences):
        """
        Computes the similarity of the preference vectors

        :param from_preferences: the preference vector of the record from which
        the similarity is directed
        :param to_preferences: the preference vector of the record to which
        the similarity is directed
        """
        raise NotImplementedError()


class JaccardSimilarity(AbstractPreferenceSimilarity):
    """
    Computes the Jaccard similarity of the two preference vectors
    """

    def get_similarity(self, from_preferences, to_preferences):
        """
        Computes the jaccard similarity of the preference vectors

        :param from_preferences: the preference vector of the record from which
        the similarity is directed
        :param to_preferences: the preference vector of the record to which
        the similarity is directed
        """
        return jaccard_sim(
            from_preferences.keys(), to_preferences.keys())


class CosineSimilarity(AbstractPreferenceSimilarity):
    """
    Computes the cosine similarity of the two preference vectors
    """

    def get_similarity(self, from_preferences, to_preferences):
        """
        Computes the cosine similarity of the preference vectors

        :param from_preferences: the preference vector of the record from which
        the similarity is directed
        :param to_preferences: the preference vector of the record to which
        the similarity is directed
        """
        return cosine_sim(
            {key: pref.value for key, pref in from_preferences.iteritems()},
            {key: pref.value for key, pref in to_preferences.iteritems()},
        )


class SignificanceWeighting(AbstractPreferenceSimilarity):
    """
    Penalises the similarity of the underlying similarity_metric if it is
    based on few overlaps in terms of the preference vectors
    """
    def __init__(self, similarity_metric, min_overlap):
        self.similarity_metric = similarity_metric
        self.min_overlap = min_overlap

    def get_similarity(self, from_preferences, to_preferences):
        """
        Penalises the similarity of the underlying similarity_metric if it is
        based on few overlaps in terms of the preference vectors

        :param from_preferences: the preference vector of the record from which
        the similarity is directed
        :param to_preferences: the preference vector of the record to which
        the similarity is directed
        """
        similarity = self.similarity_metric.get_similarity(
            from_preferences, to_preferences)
        overlap = len(
            set(from_preferences.iterkeys()) & set(to_preferences.iterkeys()))
        weight = min(overlap, self.min_overlap) / float(self.min_overlap)
        return similarity * weight


def partition_preferences_by_time(
        preferences, time_bounds):
    time_parts = [{} for _ in xrange(len(time_bounds))]
    for key, pref in preferences.iteritems():
        for t, time_bound in enumerate(time_bounds):
            if pref.preference_time > time_bound:
                time_parts[t][key] = pref
                break
    return time_parts


class TimeDecaySimilarity(AbstractPreferenceSimilarity):
    """
    Implements a decreasing weight that penalises older interactions
    """
    def __init__(
            self, similarity_metric,
            time_interval=timedelta(weeks=8), half_life=2,
            max_age=12):
        """
        :param similarity_metric: The underlying similarity metric that is
        called with every partition of preference values
        :param time_interval: The interval with which the preferences are
        partitioned
        :param half_life: The number of intervals until the weight is half of
        its initial value
        :param max_age: The max number of intervals to consider
        """
        self.similarity_metric = similarity_metric
        self.time_interval = time_interval
        self.half_life = half_life
        self.max_age = max_age

    def get_similarity(self, from_preferences, to_preferences):
        """
        Implements a decreasing weight that penalises older interactions

        :param from_preferences: the preference vector of the record from which
        the similarity is directed
        :param to_preferences: the preference vector of the record to which
        the similarity is directed
        """
        if len(from_preferences) == 0 and len(to_preferences) == 0:
            return float('NaN')

        time_bounds = []
        time_weights = []
        weight_sum = 0.0
        curr = utcnow()
        for t in xrange(self.max_age):
            curr -= self.time_interval
            time_bounds.append(curr)
            weight = 2**(-(t)/float(self.half_life))
            weight_sum += weight
            time_weights.append(weight)

        from_parts = partition_preferences_by_time(
            from_preferences, time_bounds)

        to_parts = partition_preferences_by_time(
            to_preferences, time_bounds)

        sim_sum = 0.0
        for t, w in enumerate(time_weights):
            sim = self.similarity_metric.get_similarity(
                from_parts[t], to_parts[t])
            if not math.isnan(sim):
                sim_sum += w*sim

        return sim_sum / weight_sum
