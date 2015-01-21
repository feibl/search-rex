from test_base import BaseTestCase
from search_rex.services import report_action
from search_rex.services import set_record_active
from search_rex.recommendations.queries import get_actions_on_records
from search_rex.recommendations.queries import get_actions_on_record
from search_rex.recommendations.queries import get_actions_of_session
from search_rex.recommendations.queries import get_records
from search_rex.models import ActionType
from datetime import datetime
from datetime import timedelta

from search_rex.util import date_util
import mock


def insert_external_view_action(session, record):
    insert_action(session, record, ActionType.view, False)


def insert_action(
        session, record, action_type=ActionType.view, is_internal=False,
        timestamp=datetime(1999, 1, 1)):
    report_action(
        record_id=record,
        timestamp=timestamp,
        session_id=session,
        is_internal_record=is_internal,
        action_type=action_type)


class GetHitsForQueryTestCase(BaseTestCase):

    def setUp(self):
        super(GetHitsForQueryTestCase, self).setUp()

    def test__get_records__include_internal_records_is_true(self):
        include_internal_records = True
        record_caesar = 'caesar'
        record_brutus = 'brutus'
        record_napoleon = 'napoleon'
        session_alice = 'alice'
        session_bob = 'bob'
        expected_records = [record_caesar, record_brutus, record_napoleon]

        insert_action(session_alice, record_caesar, is_internal=True)
        insert_action(session_bob, record_brutus, is_internal=False)
        insert_action(session_bob, record_napoleon, is_internal=False)

        ret_records = list(get_records(include_internal_records))
        assert sorted(expected_records) == sorted(ret_records)

    def test__get_records__include_internal_records_is_false(self):
        include_internal_records = False
        record_caesar = 'caesar'
        record_brutus = 'brutus'
        record_napoleon = 'napoleon'
        session_alice = 'alice'
        session_bob = 'bob'
        expected_records = [record_brutus, record_napoleon]

        insert_action(session_alice, record_caesar, is_internal=True)
        insert_action(session_bob, record_brutus, is_internal=False)
        insert_action(session_bob, record_napoleon, is_internal=False)

        ret_records = list(get_records(include_internal_records))
        assert sorted(expected_records) == sorted(ret_records)

    def test__get_actions_of_session(self):
        record_caesar = 'caesar'
        record_brutus = 'brutus'
        record_napoleon = 'napoleon'
        expected_actions = [
            (record_caesar, ActionType.view),
            (record_brutus, ActionType.view),
            (record_brutus, ActionType.copy),
            (record_napoleon, ActionType.view),
        ]

        session_alice = 'alice'

        for record, action_type in expected_actions:
            insert_action(session_alice, record, action_type=action_type)

        actions = list(get_actions_of_session(session_alice))

        assert len(actions) == 4

        for record, action_type in expected_actions:
            assert any(filter(
                lambda a: a.record_id == record and
                a.action_type == action_type,
                actions))

    def test__get_actions_of_session__session_not_present__empty_list(self):
        session_unknown = 'random'
        actions = list(get_actions_of_session(session_unknown))
        assert len(actions) == 0

    def test__get_actions_on_record(self):
        record_caesar = 'caesar'
        session_alice = 'alice'
        session_bob = 'bob'
        session_carol = 'carol'
        expected_actions = [
            (session_alice, ActionType.view),
            (session_bob, ActionType.view),
            (session_bob, ActionType.copy),
            (session_carol, ActionType.view),
        ]

        for session, action_type in expected_actions:
            insert_action(session, record_caesar, action_type=action_type)

        actions = list(get_actions_on_record(record_caesar))

        assert len(actions) == 4

        for session, action_type in expected_actions:
            assert any(filter(
                lambda a: a.session_id == session and
                a.action_type == action_type,
                actions))

    def test__get_actions_on_record__actions_older_max_age_ignored(self):
        record_caesar = 'caesar'
        session_alice = 'alice'
        insert_action(
            session_alice, record_caesar, timestamp=datetime(1999, 1, 1))

        date_util._utcnow = mock.Mock(return_value=datetime(1999, 1, 3))

        actions = list(
            get_actions_on_record(record_caesar, max_age=timedelta(days=1)))
        assert len(actions) == 0

    def test__get_actions_on_record__record_not_present__empty_list(self):
        record_unknown = 'random'
        actions = list(get_actions_on_record(record_unknown))
        assert len(actions) == 0

    def test__get_actions_on_records__include_internal_records_is_true(self):
        include_internal_records = True
        record_caesar = 'caesar'
        record_brutus = 'brutus'
        record_napoleon = 'napoleon'
        session_alice = 'alice'
        session_bob = 'bob'
        session_carol = 'carol'
        is_internal = {
            record_caesar: True,
            record_brutus: False,
            record_napoleon: False,
        }

        actions = [
            (session_alice, record_caesar, ActionType.view),
            (session_bob, record_caesar, ActionType.view),
            (session_bob, record_brutus, ActionType.copy),
            (session_carol, record_napoleon, ActionType.view),
        ]

        for session, record, action_type in actions:
            insert_action(
                session, record, action_type=action_type,
                is_internal=is_internal[record])

        expected_actions = {
            record_caesar: [actions[0], actions[1]],
            record_brutus: [actions[2]],
            record_napoleon: [actions[3]],
        }

        actions = list(get_actions_on_records(include_internal_records))
        actions = {record: rec_actions for record, rec_actions in actions}

        assert len(actions) == len(expected_actions)

        for record, rec_actions in expected_actions.iteritems():
            for session, _, action_type in rec_actions:
                assert any(filter(
                    lambda a: a.session_id == session and
                    a.action_type == action_type,
                    actions[record]))

    def test__get_actions_on_records__include_internal_records_is_false(self):
        include_internal_records = False
        record_caesar = 'caesar'
        record_brutus = 'brutus'
        record_napoleon = 'napoleon'
        session_alice = 'alice'
        session_bob = 'bob'
        session_carol = 'carol'
        is_internal = {
            record_caesar: True,
            record_brutus: False,
            record_napoleon: False,
        }

        actions = [
            (session_alice, record_caesar, ActionType.view),
            (session_bob, record_caesar, ActionType.view),
            (session_bob, record_brutus, ActionType.copy),
            (session_carol, record_napoleon, ActionType.view),
        ]

        for session, record, action_type in actions:
            insert_action(
                session, record, action_type=action_type,
                is_internal=is_internal[record])

        expected_actions = {
            record_brutus: [actions[2]],
            record_napoleon: [actions[3]],
        }

        actions = list(get_actions_on_records(include_internal_records))
        actions = {record: rec_actions for record, rec_actions in actions}

        assert len(actions) == len(expected_actions)

        for record, rec_actions in expected_actions.iteritems():
            for session, _, action_type in rec_actions:
                assert any(filter(
                    lambda a: a.session_id == session and
                    a.action_type == action_type,
                    actions[record]))

    def test__get_actions_on_records__actions_older_than_max_age_ignored(self):
        record_caesar = 'caesar'
        session_alice = 'alice'
        session_bob = 'bob'
        insert_action(
            session_alice, record_caesar, timestamp=datetime(1999, 1, 1))
        insert_action(
            session_bob, record_caesar, timestamp=datetime(1999, 1, 3))

        date_util._utcnow = mock.Mock(return_value=datetime(1999, 1, 3))

        actions = list(
            get_actions_on_records(record_caesar, max_age=timedelta(days=1)))
        assert len(actions) == 1

        record, rec_actions = actions[0]
        assert len(rec_actions) == 1
        assert rec_actions[0].session_id == session_bob

    def test__get_actions_on_records__actions_on_deactivated_records_not_returned(self):
        session_alice = 'alice'
        record_caesar = 'caesar'

        insert_action(session_alice, record_caesar)
        set_record_active(record_caesar, active=False)

        actions = list(get_actions_on_records(True))

        assert len(actions) == 0
