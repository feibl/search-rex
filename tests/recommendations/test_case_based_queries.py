from test_base import BaseTestCase
from search_rex.models import ActionType
from search_rex.recommendations import queries
from search_rex.services import report_action
from search_rex.services import set_record_active
from datetime import datetime
from datetime import timedelta

from search_rex.util import date_util
import mock


def insert_external_view_action(query, record):
    insert_action(query, record, ActionType.view, False)


def insert_action(
        query, record, action_type, is_internal,
        timestamp=datetime(1999, 1, 1)):
    report_action(
        record_id=record,
        timestamp=timestamp,
        session_id='alice',
        is_internal_record=is_internal,
        action_type=action_type,
        query_string=query)


class GetHitsForQueryTestCase(BaseTestCase):

    def setUp(self):
        super(GetHitsForQueryTestCase, self).setUp()

    def test__get_queries(self):
        query_rome = 'rome'
        query_caesar = 'caesar'
        record_caesar = 'caesar'
        record_brutus = 'brutus'
        expected_queries = [query_rome, query_caesar]

        insert_external_view_action(query_rome, record_caesar)
        insert_external_view_action(query_caesar, record_brutus)

        assert sorted(expected_queries) == sorted(list(queries.get_queries()))

    def test__get_actions_for_queries__include_internal_records__one_hit_one_query(self):
        query_rome = 'rome'
        record_caesar = 'caesar'
        action_type = ActionType.view
        include_internal_records = True

        insert_action(query_rome, record_caesar, action_type, False)

        actions = list(queries.get_actions_for_queries(
            include_internal_records=include_internal_records))

        assert len(actions) == 1
        query, q_actions = actions[0]

        assert query == query_rome
        assert len(q_actions) == 1
        assert q_actions[0].record_id == record_caesar
        assert q_actions[0].action_type == action_type

    def test__get_actions_for_queries__include_internal_records__two_hit_one_query(self):
        query_rome = 'rome'
        record_caesar = 'caesar'
        record_brutus = 'brutus'
        action_type = ActionType.view
        include_internal_records = True

        insert_action(query_rome, record_caesar, action_type, False)
        insert_action(query_rome, record_brutus, action_type, False)

        actions = list(queries.get_actions_for_queries(
            include_internal_records=include_internal_records))

        assert len(actions) == 1
        query, q_actions = actions[0]

        assert query == query_rome
        assert len(q_actions) == 2
        assert any(filter(lambda a: a.record_id == record_caesar, q_actions))
        assert any(filter(lambda a: a.record_id == record_brutus, q_actions))

    def test__get_actions_for_queries__include_internal_records__two_hit_two_query(self):
        query_rome = 'rome'
        query_caesar = 'caesar'
        record_brutus = 'brutus'
        record_caesar = 'caesar'
        action_type = ActionType.view
        include_internal_records = True

        insert_action(query_rome, record_brutus, action_type, False)
        insert_action(query_caesar, record_caesar, action_type, False)

        actions = list(queries.get_actions_for_queries(
            include_internal_records=include_internal_records))

        assert len(actions) == 2
        s_actions = sorted(actions, key=lambda (k, v): k)

        assert s_actions[0][0] == query_caesar
        assert s_actions[1][0] == query_rome

    def test__get_actions_for_queries__exclude_internal_records__internal_action_not_returned(self):
        query_rome = 'rome'
        record_caesar = 'caesar'
        action_type = ActionType.view
        include_internal_records = False

        insert_action(query_rome, record_caesar, action_type, True)

        actions = list(queries.get_actions_for_queries(
            include_internal_records=include_internal_records))

        assert len(actions) == 0

    def test__get_actions_for_queries__pass_queries(self):
        query_rome = 'rome'
        query_caesar = 'caesar'
        record_brutus = 'brutus'
        record_caesar = 'caesar'
        action_type = ActionType.view
        include_internal_records = True

        insert_action(query_rome, record_brutus, action_type, False)
        insert_action(query_caesar, record_caesar, action_type, False)

        actions = list(queries.get_actions_for_queries(
            include_internal_records=include_internal_records,
            query_strings=[query_rome]))

        assert len(actions) == 1

        assert actions[0][0] == query_rome

    def test__get_actions_for_queries__actions_on_deactivated_records_not_returned(self):
        query_rome = 'rome'
        record_caesar = 'caesar'
        action_type = ActionType.view
        include_internal_records = True

        insert_action(query_rome, record_caesar, action_type, True)
        set_record_active(record_caesar, active=False)

        actions = list(queries.get_actions_for_queries(
            include_internal_records=include_internal_records))

        assert len(actions) == 0

    def test__get_actions_for_queries__actions_older_than_max_age_ignored(self):
        query_rome = 'rome'
        record_caesar = 'caesar'
        action_type = ActionType.view
        include_internal_records = True

        date_util._utcnow = mock.Mock(return_value=datetime(1999, 1, 3))
        insert_action(
            query_rome, record_caesar, action_type, True,
            datetime(1999, 1, 1))

        actions = list(queries.get_actions_for_queries(
            include_internal_records=include_internal_records,
            max_age=timedelta(days=1)))

        assert len(actions) == 0
