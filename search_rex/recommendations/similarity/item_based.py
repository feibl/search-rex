from similarity_metrics import jaccard_sim
from similarity_metrics import cosine_sim


class AbstractRecordSimilarity(object):
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

    def get_similarity(self, from_record_id, to_record_id):
        from_preferences = self.data_model.get_preferences_for_record(
            from_record_id)
        to_preferences = self.data_model.get_preferences_for_record(
            to_record_id)
        return self.similarity_metric.get_similarity(
            from_preferences, to_preferences)


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
