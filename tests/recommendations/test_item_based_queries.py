from test_base import BaseTestCase
from datetime import datetime
from search_rex.services import report_action
from search_rex.services import set_record_active
from search_rex.recommendations.queries import get_actions_on_records
from search_rex.recommendations.queries import get_actions_on_record
from search_rex.recommendations.queries import get_actions_of_session
from search_rex.recommendations.queries import get_records
from search_rex.models import ActionType
import os

_cwd = os.path.dirname(os.path.abspath(__file__))


session_alice = 'alice'
session_bob = 'bob'
session_carol = 'carol'
session_dave = 'dave'
session_eric = 'eric'

record_napoleon = 'napoleon'
record_caesar = 'caesar'
record_brutus = 'brutus'
record_secrets_of_rome = 'secrets_of_rome'
record_cleopatra = 'cleopatra'
record_inactive = 'inactive'

is_internal = {
    record_napoleon: False,
    record_caesar: False,
    record_brutus: False,
    record_secrets_of_rome: True,
    record_cleopatra: False,
    record_inactive: False,
}

is_active = {
    record_napoleon: True,
    record_caesar: True,
    record_brutus: True,
    record_secrets_of_rome: True,
    record_cleopatra: True,
    record_inactive: False,
}

time_created = datetime(1999, 1, 1)


def import_test_data():
    test_data_path = os.path.join(_cwd, 'resource', 'item_based_test_data.csv')
    with open(test_data_path, 'r') as td_file:
        lines = td_file.readlines()
        for i_line, line in enumerate(lines):
            line = line.strip()
            if i_line == 0:
                # Header
                continue
            if line == '':
                # Filler
                continue
            session_id, record_id, action_type = line.split(',')

            report_action(
                record_id=record_id,
                timestamp=datetime(1999, 1, 1),
                session_id=session_id,
                is_internal_record=is_internal[record_id],
                action_type=action_type)

        for record_id, active in is_active.iteritems():
            set_record_active(record_id=record_id, active=active)


class GetRecordsTestCase(BaseTestCase):

    def setUp(self):
        super(GetRecordsTestCase, self).setUp()

        import_test_data()

    def test__get_records__include_internal_is_false(self):
        include_internal_records = False
        expected_records = [
            record_caesar,
            record_cleopatra,
            record_brutus,
            record_napoleon,
        ]

        returned_records = list(get_records(
            include_internal_records=include_internal_records))
        assert sorted(returned_records) == sorted(expected_records)

    def test__get_records__include_internal_records_is_true(self):
        include_internal_records = True
        expected_records = [
            record_caesar,
            record_cleopatra,
            record_brutus,
            record_napoleon,
            record_secrets_of_rome,
        ]

        returned_records = list(get_records(
            include_internal_records=include_internal_records))
        assert sorted(returned_records) == sorted(expected_records)

    def test__get_viewed_records(self):
        session_id = session_alice

        expected_actions = [
            (record_caesar, ActionType.view),
            (record_brutus, ActionType.view),
            (record_caesar, ActionType.copy),
            (record_brutus, ActionType.copy),
            (record_secrets_of_rome, ActionType.copy),
        ]

        returned_actions = list(get_actions_of_session(session_id=session_id))

        returned_actions = [
            (action.record_id, action.action_type) for action in
            returned_actions
        ]

        assert sorted(returned_actions) == sorted(expected_actions)

    def test__get_that_records__unknown_session__empty_list(self):
        session_id = 'mallory'

        returned_actions = list(get_actions_of_session(session_id=session_id))

        assert len(returned_actions) == 0

    def test__sessions_that_viewed_records(self):
        record_id = record_caesar

        expected_actions = [
            (session_alice, ActionType.view),
            (session_bob, ActionType.view),
            (session_dave, ActionType.view),
            (session_alice, ActionType.copy),
            (session_dave, ActionType.copy),
        ]

        returned_actions = list(get_actions_on_record(record_id=record_id))

        returned_actions = [
            (action.session_id, action.action_type) for action in
            returned_actions
        ]

        assert sorted(expected_actions) == sorted(returned_actions)

    def test__sessions_that_seen_record__unknown_record__empty_list(self):
        record_id = 'dogma'

        returned_actions = list(get_actions_on_record(record_id=record_id))

        assert len(returned_actions) == 0

    def test__get_actions_on_records__do_not_include_internal_records(self):
        include_internal_records = False

        expected_actions = [
            (record_caesar, [
                (session_alice, ActionType.view),
                (session_bob, ActionType.view),
                (session_dave, ActionType.view),
                (session_alice, ActionType.copy),
                (session_dave, ActionType.copy),
            ]),
            (record_brutus, [
                (session_alice, ActionType.view),
                (session_bob, ActionType.view),
                (session_alice, ActionType.copy),
                (session_bob, ActionType.copy),
            ]),
            (record_cleopatra, [
                (session_bob, ActionType.view),
                (session_carol, ActionType.view),
                (session_bob, ActionType.copy),
            ]),
            (record_napoleon, [
                (session_eric, ActionType.view),
                (session_dave, ActionType.copy),
                (session_eric, ActionType.copy),
            ]),
        ]

        returned_actions = list(
            get_actions_on_records(include_internal_records))

        expected_actions = sorted(expected_actions)
        returned_actions = sorted(returned_actions)

        assert len(returned_actions) == len(expected_actions)
        for i in range(len(expected_actions)):
            assert returned_actions[i][0] == expected_actions[i][0]
            actions_on_record = [
                (action.session_id, action.action_type) for action in
                returned_actions[i][1]
            ]
            assert sorted(actions_on_record) ==\
                sorted(expected_actions[i][1])

    def test__get_actions_on_records__include_internal_records(self):
        include_internal_records = True

        expected_actions = [
            (record_caesar, [
                (session_alice, ActionType.view),
                (session_bob, ActionType.view),
                (session_dave, ActionType.view),
                (session_alice, ActionType.copy),
                (session_dave, ActionType.copy),
            ]),
            (record_brutus, [
                (session_alice, ActionType.view),
                (session_bob, ActionType.view),
                (session_alice, ActionType.copy),
                (session_bob, ActionType.copy),
            ]),
            (record_cleopatra, [
                (session_bob, ActionType.view),
                (session_carol, ActionType.view),
                (session_bob, ActionType.copy),
            ]),
            (record_napoleon, [
                (session_eric, ActionType.view),
                (session_dave, ActionType.copy),
                (session_eric, ActionType.copy),
            ]),
            (record_secrets_of_rome, [
                (session_alice, ActionType.copy),
                (session_dave, ActionType.view),
                (session_dave, ActionType.copy),
            ]),
        ]
        returned_actions = list(
            get_actions_on_records(include_internal_records))

        expected_actions = sorted(expected_actions)
        returned_actions = sorted(returned_actions)

        assert len(returned_actions) == len(expected_actions)
        for i in range(len(expected_actions)):
            assert returned_actions[i][0] == expected_actions[i][0]
            actions_on_record = [
                (action.session_id, action.action_type) for action in
                returned_actions[i][1]
            ]
            assert sorted(actions_on_record) ==\
                sorted(expected_actions[i][1])
