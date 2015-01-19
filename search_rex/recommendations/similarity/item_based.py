from similarity_metrics import jaccard_sim


class AbstractRecordSimilarity(object):
    """
    Computes the similarity from one record to the other
    """

    def get_similarity(self, from_record_id, to_record_id):
        raise NotImplementedError()


class JaccardRecordSimilarity(object):
    """
    Computes the Jaccard similarity of the two records' interactions
    """

    def __init__(self, data_model):
        self.data_model = data_model

    def get_similarity(self, from_record_id, to_record_id):
        from_preferences = self.data_model.get_preferences_for_record(
            from_record_id)
        to_preferences = self.data_model.get_preferences_for_record(
            to_record_id)

        return jaccard_sim(
            from_preferences.keys(), to_preferences.keys())
