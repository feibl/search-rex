from test_base import BaseTestCase
from search_rex.recommendations import create_recommender_system
from search_rex.recommendations.data_model.item_based import\
    InMemoryRecordDataModel
from search_rex.recommendations.data_model.item_based import\
    PersistentRecordDataModel
from search_rex.recommendations.neighbourhood.item_based import\
    KNearestRecordNeighbourhood
from search_rex.recommendations.similarity.item_based import\
    JaccardSimilarity
from search_rex.recommendations.similarity.item_based import\
    RecordSimilarity
from search_rex.recommendations.recommenders.item_based import\
    RecordBasedRecommender
from search_rex.recommendations import refresh_recommenders
import os
from datetime import datetime
from tests.resource.item_based_data import *

_cwd = os.path.dirname(os.path.abspath(__file__))


def create_record_based_recommender(include_internal_records):
    data_model = PersistentRecordDataModel(
        include_internal_records)
    in_mem_dm = InMemoryRecordDataModel(data_model)
    pref_sim = JaccardSimilarity()
    record_sim = RecordSimilarity(in_mem_dm, pref_sim)
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


class RecordBasedRecommenderTestCase(BaseTestCase):

    def setUp(self):
        super(RecordBasedRecommenderTestCase, self).setUp()
        create_recommender_system(self.app)

    def influenced_by_your_history(
            self, session_id, include_internal_records,
            max_num_recs=10):
        client, app = self.client, self.app

        url = base_url + '/influenced_by_your_history'
        request = create_request(url, dict(
            session_id=session_id,
            include_internal_records=include_internal_records,
            api_key=app.config['API_KEY'],
            max_num_recs=max_num_recs)
        )
        print(request)
        rv = client.get(request)
        print(rv)
        return [e['record_id'] for e in rv.json['results']]

    def other_users_also_used(
            self, record_id, include_internal_records,
            max_num_recs=10):
        client, app = self.client, self.app

        url = base_url + '/other_users_also_used'
        request = create_request(url, dict(
            record_id=record_id,
            include_internal_records=include_internal_records,
            api_key=app.config['API_KEY'],
            max_num_recs=max_num_recs)
        )
        print(request)
        rv = client.get(request)

        print(rv)
        return [e['record_id'] for e in rv.json['results']]

    def test__influenced_by_your_history__exclude_internal_documents(self):
        views = view_actions
        copies = copy_actions
        include_internal_records = False

        import_test_data(
            views=views, copies=copies, timestamp=datetime.utcnow())
        refresh_recommenders()

        recs = self.influenced_by_your_history(
            session_alice, include_internal_records)
        assert list(recs) == [record_cleopatra, record_napoleon]

        recs = self.influenced_by_your_history(
            session_bob, include_internal_records)
        assert list(recs) == [record_napoleon]

        recs = self.influenced_by_your_history(
            session_carol, include_internal_records)
        assert list(recs) == [record_caesar, record_brutus, record_napoleon]

        recs = self.influenced_by_your_history(
            session_dave, include_internal_records)
        assert list(recs) == [record_brutus, record_cleopatra, record_napoleon]

        recs = self.influenced_by_your_history(
            session_dave, include_internal_records, max_num_recs=2)
        assert list(recs) == [record_brutus, record_cleopatra]

        recs = self.influenced_by_your_history(
            session_eric, include_internal_records)
        assert list(recs) == [
            record_caesar, record_brutus, record_cleopatra]

        # No Similar Records -> no recommendations
        recs = self.influenced_by_your_history(
            session_isolated, include_internal_records)
        assert list(recs) == []

        # Has seen all records -> no recommendations
        recs = self.influenced_by_your_history(
            session_seen_all, include_internal_records)
        assert list(recs) == []

        # Has seen no records -> no recommendations
        recs = self.influenced_by_your_history(
            session_seen_nothing, include_internal_records)
        assert list(recs) == []

    def test__influenced_by_your_history__include_internal_documents(self):
        views = view_actions
        copies = copy_actions
        include_internal_records = True

        import_test_data(
            views=views, copies=copies, timestamp=datetime.utcnow())
        refresh_recommenders()

        recs = self.influenced_by_your_history(
            session_alice, include_internal_records)
        assert list(recs) == [
            record_cleopatra, record_secrets_of_rome, record_napoleon]

        recs = self.influenced_by_your_history(
            session_bob, include_internal_records)
        assert list(recs) == [record_secrets_of_rome, record_napoleon]

        recs = self.influenced_by_your_history(
            session_carol, include_internal_records)
        assert list(recs) == [
            record_caesar, record_brutus, record_secrets_of_rome,
            record_napoleon]

        recs = self.influenced_by_your_history(
            session_dave, include_internal_records)
        assert list(recs) == [
            record_brutus, record_cleopatra, record_napoleon]

        recs = self.influenced_by_your_history(
            session_dave, include_internal_records, max_num_recs=2)
        assert list(recs) == [record_brutus, record_cleopatra]

        recs = self.influenced_by_your_history(
            session_eric, include_internal_records)
        assert list(recs) == [
            record_caesar, record_brutus, record_cleopatra,
            record_secrets_of_rome]

        # No Similar Records -> no recommendations
        recs = self.influenced_by_your_history(
            session_isolated, include_internal_records)
        assert list(recs) == []

        # Has seen all records -> no recommendations
        recs = self.influenced_by_your_history(
            session_seen_all, include_internal_records)
        assert list(recs) == []

        # Has seen no records -> no recommendations
        recs = self.influenced_by_your_history(
            session_seen_nothing, include_internal_records)
        assert list(recs) == []

    def test__other_users_also_used__exclude_internal_documents(self):
        views = view_actions
        copies = copy_actions
        include_internal_records = False

        import_test_data(
            views=views, copies=copies, timestamp=datetime.utcnow())
        refresh_recommenders()

        recs = self.other_users_also_used(
            record_welcome, include_internal_records)
        assert list(recs) == [
            record_caesar, record_brutus, record_cleopatra,
            record_napoleon]

        recs = self.other_users_also_used(
            record_caesar, include_internal_records)
        assert list(recs) == [
            record_welcome, record_brutus, record_cleopatra,
            record_napoleon]

        recs = self.other_users_also_used(
            record_caesar, include_internal_records, max_num_recs=2)
        assert list(recs) == [
            record_welcome, record_brutus]

        recs = self.other_users_also_used(
            record_brutus, include_internal_records)
        assert list(recs) == [
            record_caesar, record_welcome, record_cleopatra,
            record_napoleon]

        recs = self.other_users_also_used(
            record_isolated, include_internal_records)
        assert list(recs) == []

    def test__similar_records__include_internal_documents(self):
        views = view_actions
        copies = copy_actions
        include_internal_records = True

        import_test_data(
            views=views, copies=copies, timestamp=datetime.utcnow())
        refresh_recommenders()

        recs = self.other_users_also_used(
            record_welcome, include_internal_records)
        assert list(recs) == [
            record_caesar, record_brutus, record_cleopatra,
            record_secrets_of_rome, record_napoleon]

        recs = self.other_users_also_used(
            record_caesar, include_internal_records)
        assert list(recs) == [
            record_welcome, record_brutus, record_cleopatra,
            record_secrets_of_rome, record_napoleon]

        recs = self.other_users_also_used(
            record_caesar, include_internal_records, max_num_recs=2)
        assert list(recs) == [
            record_welcome, record_brutus]

        recs = self.other_users_also_used(
            record_brutus, include_internal_records)
        assert list(recs) == [
            record_caesar, record_welcome, record_cleopatra,
            record_napoleon, record_secrets_of_rome]

        recs = self.other_users_also_used(
            record_isolated, include_internal_records)
        assert list(recs) == []
