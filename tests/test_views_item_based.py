from test_base import BaseTestCase
from search_rex.recommendations import create_recommender_system
from search_rex.recommendations.data_model.item_based import\
    InMemoryRecordDataModel
from search_rex.recommendations.data_model.item_based import\
    PersistentRecordDataModel
from search_rex.recommendations.neighbourhood.item_based import\
    KNearestRecordNeighbourhood
from search_rex.recommendations.similarity.item_based import\
    JaccardRecordSimilarity
from search_rex.recommendations.recommenders.item_based import\
    RecordBasedRecommender
import os
from tests.resource import item_based_data

_cwd = os.path.dirname(os.path.abspath(__file__))


def create_record_based_recommender(include_internal_records):
    data_model = PersistentRecordDataModel(
        include_internal_records)
    in_mem_dm = InMemoryRecordDataModel(data_model)
    record_sim = JaccardRecordSimilarity(in_mem_dm)
    record_nhood = KNearestRecordNeighbourhood(10, in_mem_dm, record_sim)
    record_based_recsys = RecordBasedRecommender(
        data_model, record_nhood, record_sim)

    return record_based_recsys


base_url = '/api'


def create_request(route, parameters):
    return '{}?{}'.format(
        route,
        '&'.join(['{}={}'.format(k, v) for k, v in parameters.items()])
    )


def inspired_by_your_history(
        client, app, session_id, include_internal_records):
    url = base_url + '/inspired_by_your_history'

    rv = client.get(create_request(url, dict(
        session_id=session_id,
        include_internal_records=include_internal_records,
        api_key=app.config['API_KEY']
    )))
    return [(e['record_id'], e['score']) for e in rv.json['results']]


class RecordBasedRecommenderTestCase(BaseTestCase):

    def setUp(self):
        super(RecordBasedRecommenderTestCase, self).setUp()

    def test__inspired_by_your_history__exclude_internal_documents(self):
        views = item_based_data.view_actions
        copies = item_based_data.copy_actions
        include_internal_records = False

        item_based_data.import_test_data(views=views, copies=copies)

        create_recommender_system(
            self.app, create_record_based_recommender)

        recs, _ = zip(*inspired_by_your_history(
            self.client, self.app, item_based_data.session_alice,
            include_internal_records))
        assert list(recs) == [
            item_based_data.record_cleopatra,
            item_based_data.record_napoleon]
