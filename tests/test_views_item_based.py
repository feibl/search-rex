from test_base import BaseTestCase
from search_rex.core import db
from datetime import datetime
from search_rex.services import set_record_active
from search_rex.services import report_view_action
from search_rex.services import report_copy_action
from search_rex.recommendations import create_recommender_system
from search_rex.models import ActionType
from search_rex.recommendations.data_model.item_based import\
    InMemoryRecordBasedDataModel
from search_rex.recommendations.data_model.item_based import\
    RecordBasedDataModel
from search_rex.recommendations.neighbourhood.item_based import\
    KNearestRecordNeighbourhood
from search_rex.recommendations.similarity.item_based import\
    JaccardRecordSimilarity
from search_rex.recommendations.recommenders.item_based import\
    RecordBasedRecommender
from search_rex.recommendations import Recommender
import os

_cwd = os.path.dirname(os.path.abspath(__file__))


session_alice = 'alice'
session_bob = 'bob'
session_carol = 'carol'
session_dave = 'dave'
session_eric = 'eric'
session_frank = 'frank'
session_garry = 'garry'
session_hally = 'hally'
session_ian = 'ian'
session_isolated = 'isolated'
session_seen_all = 'seen all'
session_seen_nothing = 'seen nothing'

record_welcome = 'welcome'
record_napoleon = 'napoleon'
record_caesar = 'caesar'
record_brutus = 'brutus'
record_secrets_of_rome = 'secrets_of_rome'
record_cleopatra = 'cleopatra'
record_inactive = 'inactive'
record_isolated = 'isolated'

is_internal = {
    record_welcome: False,
    record_napoleon: False,
    record_caesar: False,
    record_brutus: False,
    record_cleopatra: False,
    record_inactive: False,
    record_isolated: False,
    record_secrets_of_rome: True,
}

is_active = {
    record_welcome: True,
    record_napoleon: True,
    record_caesar: True,
    record_brutus: True,
    record_secrets_of_rome: True,
    record_cleopatra: True,
    record_isolated: True,
    record_inactive: False,
}

test_actions = {
    session_alice: [
        record_welcome, record_caesar, record_brutus, record_inactive],
    session_bob: [
        record_welcome, record_caesar, record_brutus, record_cleopatra],
    session_carol: [
        record_welcome, record_cleopatra],
    session_dave: [
        record_welcome, record_caesar, record_secrets_of_rome],
    session_eric: [
        record_welcome, record_napoleon],
    session_frank: [
        record_welcome, record_caesar, record_brutus],
    session_garry: [
        record_welcome, record_caesar, record_cleopatra],
    session_hally: [
        record_welcome, record_brutus],
    session_ian: [
        record_welcome, record_secrets_of_rome],
    session_seen_all: [
        record_welcome, record_caesar, record_cleopatra, record_brutus,
        record_napoleon, record_secrets_of_rome, record_inactive],
    session_seen_nothing: [
        ],
    session_isolated: [
        record_isolated],
}

other_actions = {
    session_alice: [
        record_welcome, record_isolated, record_brutus, record_inactive],
    session_bob: [
        record_caesar, record_brutus, record_cleopatra],
    session_carol: [
        record_welcome, record_cleopatra],
    session_dave: [
        record_welcome, record_caesar, record_secrets_of_rome],
    session_eric: [
        record_welcome, record_napoleon],
    session_frank: [
        record_welcome, record_caesar],
    session_garry: [
        record_caesar, record_cleopatra],
    session_hally: [
        record_welcome, record_brutus],
    session_ian: [
        record_welcome, record_secrets_of_rome],
    session_seen_all: [
        record_caesar, record_cleopatra, record_brutus,
        record_napoleon, record_inactive],
    session_seen_nothing: [
        ],
    session_isolated: [
        record_isolated, record_inactive, record_cleopatra],
}


def import_test_data(views, copies):
    for session_id, viewed_records in views.iteritems():
        for record_id in viewed_records:
            report_view_action(
                record_id=record_id,
                timestamp=datetime(1999,1,1),
                session_id=session_id,
                is_internal_record=is_internal[record_id])

    for session_id, copied_records in copies.iteritems():
        for record_id in copied_records:
            report_copy_action(
                record_id=record_id,
                timestamp=datetime(1999,1,1),
                session_id=session_id,
                is_internal_record=is_internal[record_id])

    for record_id, active in is_active.iteritems():
        set_record_active(record_id=record_id, active=active)


def create_record_based_recommender(action_type, include_internal_records):
    data_model = RecordBasedDataModel(
        action_type, include_internal_records)
    in_mem_dm = InMemoryRecordBasedDataModel(data_model)
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
        client, app, session_id, action_type,
        include_internal_records):
    if action_type == ActionType.view:
        url = base_url + '/inspired_by_your_view_history'
    elif action_type == ActionType.copy:
        url = base_url + '/inspired_by_your_copy_history'

    rv = client.get(create_request(url, dict(
        session_id=session_id,
        include_internal_records=include_internal_records,
        api_key=app.config['API_KEY']
    )))
    return [(e['record_id'], e['score']) for e in rv.json['results']]


class RecordBasedRecommenderTestCase(object):

    def test__inspired_by_your_history__exclude_internal_documents(self):
        action_type = self.action_type
        views = self.views
        copies = self.copies
        include_internal_records = False

        import_test_data(views=views, copies=copies)

        create_recommender_system(
            self.app, create_record_based_recommender)

        recs, _ = zip(*inspired_by_your_history(
            self.client, self.app, session_alice, action_type,
            include_internal_records))
        assert list(recs) == [record_cleopatra, record_napoleon]

class ViewRecommenderTestCase(BaseTestCase, RecordBasedRecommenderTestCase):

    views = test_actions
    copies = other_actions
    action_type = ActionType.view

    def setUp(self):
        super(ViewRecommenderTestCase, self).setUp()


class CopyRecommenderTestCase(BaseTestCase, RecordBasedRecommenderTestCase):

    views = other_actions
    copies = test_actions
    action_type = ActionType.copy

    def setUp(self):
        super(CopyRecommenderTestCase, self).setUp()
