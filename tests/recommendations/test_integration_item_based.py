from test_base import BaseTestCase
from datetime import datetime
from search_rex.services import report_view_action
from search_rex.services import report_copy_action
from search_rex.services import set_record_active
from search_rex.models import ActionType
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
                timestamp=datetime(1999, 1, 1),
                session_id=session_id,
                is_internal_record=is_internal[record_id])

    for session_id, copied_records in copies.iteritems():
        for record_id in copied_records:
            report_copy_action(
                record_id=record_id,
                timestamp=datetime(1999, 1, 1),
                session_id=session_id,
                is_internal_record=is_internal[record_id])

    for record_id, active in is_active.iteritems():
        set_record_active(record_id=record_id, active=active)


def create_recommender(action_type, include_internal_records):
    data_model = PersistentRecordDataModel(
        action_type, include_internal_records)
    in_mem_dm = InMemoryRecordDataModel(data_model)
    record_sim = JaccardRecordSimilarity(in_mem_dm)
    record_nhood = KNearestRecordNeighbourhood(10, in_mem_dm, record_sim)
    record_based_recsys = RecordBasedRecommender(
        data_model, record_nhood, record_sim)

    return Recommender(record_based_recsys, None)


class RecordBasedRecommenderTestCase(object):

    def test__inspired_by_your_history__exclude_internal_documents(self):
        action_type = self.action_type
        views = self.views
        copies = self.copies
        include_internal_records = False

        import_test_data(views=views, copies=copies)

        sut = create_recommender(
            action_type=action_type,
            include_internal_records=include_internal_records)

        recs, _ = zip(*sut.recommend_from_history(session_alice))
        assert list(recs) == [record_cleopatra, record_napoleon]

        recs, _ = zip(*sut.recommend_from_history(session_bob))
        assert list(recs) == [record_napoleon]

        recs, _ = zip(*sut.recommend_from_history(session_carol))
        assert list(recs) == [record_caesar, record_brutus, record_napoleon]

        recs, _ = zip(*sut.recommend_from_history(session_dave))
        assert list(recs) == [record_brutus, record_cleopatra, record_napoleon]

        recs, _ = zip(*sut.recommend_from_history(
            session_dave, max_num_recs=2))
        assert list(recs) == [record_brutus, record_cleopatra]

        recs, _ = zip(*sut.recommend_from_history(session_eric))
        assert list(recs) == [
            record_caesar, record_brutus, record_cleopatra]

        # No Similar Records -> no recommendations
        recs = sut.recommend_from_history(session_isolated)
        assert list(recs) == []

        # Has seen all records -> no recommendations
        recs = sut.recommend_from_history(session_seen_all)
        assert list(recs) == []

        # Has seen no records -> no recommendations
        recs = sut.recommend_from_history(session_seen_nothing)
        assert list(recs) == []

    def test__inspired_by_your_history__include_internal_documents(self):
        action_type = self.action_type
        views = self.views
        copies = self.copies
        include_internal_records = True

        import_test_data(views=views, copies=copies)

        sut = create_recommender(
            action_type=action_type,
            include_internal_records=include_internal_records)

        recs, _ = zip(*sut.recommend_from_history(session_alice))
        assert list(recs) == [
            record_cleopatra, record_secrets_of_rome, record_napoleon]

        recs, _ = zip(*sut.recommend_from_history(session_bob))
        assert list(recs) == [record_secrets_of_rome, record_napoleon]

        recs, _ = zip(*sut.recommend_from_history(session_carol))
        assert list(recs) == [
            record_caesar, record_brutus, record_secrets_of_rome,
            record_napoleon]

        recs, _ = zip(*sut.recommend_from_history(session_dave))
        assert list(recs) == [
            record_brutus, record_cleopatra, record_napoleon]

        recs, _ = zip(*sut.recommend_from_history(
            session_dave, max_num_recs=2))
        assert list(recs) == [record_brutus, record_cleopatra]

        recs, _ = zip(*sut.recommend_from_history(session_eric))
        assert list(recs) == [
            record_caesar, record_brutus, record_cleopatra,
            record_secrets_of_rome]

        # No Similar Records -> no recommendations
        recs = sut.recommend_from_history(session_isolated)
        assert list(recs) == []

        # Has seen all records -> no recommendations
        recs = sut.recommend_from_history(session_seen_all)
        assert list(recs) == []

        # Has seen no records -> no recommendations
        recs = sut.recommend_from_history(session_seen_nothing)
        assert list(recs) == []

    def test__similar_records__exclude_internal_documents(self):
        action_type = self.action_type
        views = self.views
        copies = self.copies
        include_internal_records = False

        import_test_data(views=views, copies=copies)

        sut = create_recommender(
            action_type=action_type,
            include_internal_records=include_internal_records)

        recs, _ = zip(*sut.most_similar_records(record_welcome))
        assert list(recs) == [
            record_caesar, record_brutus, record_cleopatra,
            record_napoleon]

        recs, _ = zip(*sut.most_similar_records(record_caesar))
        assert list(recs) == [
            record_welcome, record_brutus, record_cleopatra,
            record_napoleon]

        recs, _ = zip(*sut.most_similar_records(record_caesar, max_num_recs=2))
        assert list(recs) == [
            record_welcome, record_brutus]

        recs, _ = zip(*sut.most_similar_records(record_brutus))
        assert list(recs) == [
            record_caesar, record_welcome, record_cleopatra,
            record_napoleon]

        recs = sut.most_similar_records(record_isolated)
        assert list(recs) == []

    def test__similar_records__include_internal_documents(self):
        action_type = self.action_type
        views = self.views
        copies = self.copies
        include_internal_records = True

        import_test_data(views=views, copies=copies)

        sut = create_recommender(
            action_type=action_type,
            include_internal_records=include_internal_records)

        recs, _ = zip(*sut.most_similar_records(record_welcome))
        assert list(recs) == [
            record_caesar, record_brutus, record_cleopatra,
            record_secrets_of_rome, record_napoleon]

        recs, _ = zip(*sut.most_similar_records(record_caesar))
        assert list(recs) == [
            record_welcome, record_brutus, record_cleopatra,
            record_secrets_of_rome, record_napoleon]

        recs, _ = zip(*sut.most_similar_records(record_caesar, max_num_recs=2))
        assert list(recs) == [
            record_welcome, record_brutus]

        recs, _ = zip(*sut.most_similar_records(record_brutus))
        assert list(recs) == [
            record_caesar, record_welcome, record_cleopatra,
            record_napoleon, record_secrets_of_rome]

        recs = sut.most_similar_records(record_isolated)
        assert list(recs) == []


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
