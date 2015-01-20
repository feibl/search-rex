from similarity_metrics import jaccard_sim
from similarity_metrics import cosine_sim
from ..refreshable import Refreshable
from ..refreshable import RefreshHelper
from search_rex.util.date import utcnow
import math
from datetime import timedelta


class AbstractRecordSimilarity(Refreshable):
    """
    Computes the similarity from one record to the other
    """

    def get_similarity(self, from_record_id, to_record_id):
        raise NotImplementedError()


class RecordSimilarity(AbstractRecordSimilarity):
    """
    Computes the similarity from one record to the other
    """

    def __init__(self, data_model, similarity_metric):
        self.data_model = data_model
        self.similarity_metric = similarity_metric
        self.refresh_helper = RefreshHelper()
        self.refresh_helper.add_dependency(data_model)

    def get_similarity(self, from_record_id, to_record_id):
        from_preferences = self.data_model.get_preferences_for_record(
            from_record_id)
        to_preferences = self.data_model.get_preferences_for_record(
            to_record_id)
        return self.similarity_metric.get_similarity(
            from_preferences, to_preferences)

    def refresh(self, refreshed_components):
        self.refresh_helper.refresh(refreshed_components)
        refreshed_components.add(self)


class AbstractPreferenceSimilarity(object):
    """
    Computes the similarity from one preference vector to the other
    """

    def get_similarity(self, from_preferences, to_preferences):
        raise NotImplementedError()


class JaccardSimilarity(AbstractPreferenceSimilarity):
    """
    Computes the Jaccard similarity of the two preference vectors
    """

    def get_similarity(self, from_preferences, to_preferences):
        return jaccard_sim(
            from_preferences.keys(), to_preferences.keys())


class CosineSimilarity(AbstractPreferenceSimilarity):
    """
    Computes the cosine similarity of the two preference vectors
    """

    def get_similarity(self, from_preferences, to_preferences):
        return cosine_sim(
            {key: pref.value for key, pref in from_preferences.iteritems()},
            {key: pref.value for key, pref in to_preferences.iteritems()},
        )


class SignificanceWeighting(AbstractPreferenceSimilarity):
    """
    Penalises the similarity when only a small overlap of common preferences
    exist
    """
    def __init__(self, similarity_metric, min_overlap):
        self.similarity_metric = similarity_metric
        self.min_overlap = min_overlap

    def get_similarity(self, from_preferences, to_preferences):
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
    Implements a decreasing weight that penalises older interactions more
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
        if len(from_preferences) == 0 and len(to_preferences) == 0:
            return float('NaN')

        time_bounds = []
        time_weights = []
        weight_sum = 0.0
        curr = utcnow()
        for t in xrange(self.max_age):
            curr -= self.time_interval
            time_bounds.append(curr)
            weight = math.exp(-(t)/float(self.half_life))
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
