class RecommenderService():

    def __init__(
            self, record_based_recsys, query_based_recsys):
        self.record_based_recsys = record_based_recsys
        self.query_based_recsys = query_based_recsys

    def get_similar_queries(self, query_string, max_num_recs=10):
        return self.query_based_recsys.get_similar_queries(
            query_string, max_num_recs)

    def recommend_search_results(self, query_string, max_num_recs=10):
        return self.query_based_recsys.recommend_search_results(
            query_string, max_num_recs)

    def get_similar_records(self, record_id, max_num_recs=10):
        return self.record_based_recsys.get_similar_records(
            record_id, max_num_recs)

    def recommend_from_history(self, session_id, max_num_recs=10):
        return self.record_based_recsys.recommend(
            session_id, max_num_recs)
