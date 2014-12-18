from test_base import BaseTestCase
from search_rex.recommender.data_model import PersistentDataModel
from search_rex.core import db
from datetime import datetime
from search_rex.recommender.models import Action
from search_rex.recommender.models import Record
from search_rex.recommender.models import ActionType
from search_rex.recommender.models import SearchQuery
from search_rex.recommender.models import SearchSession
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

is_internal = {
    record_napoleon: False,
    record_caesar: False,
    record_brutus: False,
    record_secrets_of_rome: True,
    record_cleopatra: False,
}

def import_test_data(data_model):
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

            data_model.report_action(
                record_id=record_id,
                timestamp=datetime(1999,1,1),
                session_id=session_id,
                is_internal_record=is_internal[record_id],
                action_type=action_type)

class GetRecordsTestCase(BaseTestCase):

    def setUp(self):
        super(GetRecordsTestCase, self).setUp()

        self.sut = PersistentDataModel()
        import_test_data(self.sut)

    def test__get_records__include_internal_is_false(self):
        include_internal_records = False
        expected_records = [
            record_caesar,
            record_cleopatra,
            record_brutus,
            record_napoleon,
        ]

        returned_records = list(self.sut.get_records(
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

        returned_records = list(self.sut.get_records(
                include_internal_records=include_internal_records))
        assert sorted(returned_records) == sorted(expected_records)

    def test__get_viewed_records(self):
        session_id = session_alice
        action_type = ActionType.view

        expected_records = [record_caesar, record_brutus]

        viewed_records = list(self.sut.get_seen_records(
            session_id=session_id, action_type=action_type))
        assert sorted(viewed_records) == sorted(expected_records)

    def test__get_copied_records(self):
        session_id = session_alice
        action_type = ActionType.copy

        expected_records = [
            record_caesar, record_brutus, record_secrets_of_rome]

        copied_records = list(self.sut.get_seen_records(
            session_id=session_id, action_type=action_type))
        assert sorted(copied_records) == sorted(expected_records)

    def test__get_that_records__unknown_session__empty_list(self):
        action_type = ActionType.view
        session_id = 'mallory'

        expected_records = []

        seen_records = list(self.sut.get_seen_records(
            session_id=session_id, action_type=action_type))
        assert sorted(seen_records) == sorted(expected_records)

    def test__sessions_that_viewed_records(self):
        action_type = ActionType.view
        record_id = record_caesar

        expected_sessions = [
            session_alice, session_bob, session_dave]

        sessions_that_viewed = list(self.sut.get_sessions_that_seen_record(
            record_id=record_id, action_type=action_type))
        assert sorted(sessions_that_viewed) == sorted(expected_sessions)

    def test__sessions_that_copied_records(self):
        action_type = ActionType.copy
        record_id = record_caesar

        expected_sessions = [
            session_alice, session_dave]

        sessions_that_copied = list(self.sut.get_sessions_that_seen_record(
            record_id=record_id, action_type=action_type))
        assert sorted(sessions_that_copied) == sorted(expected_sessions)

    def test__sessions_that_seen_record__unknown_record__empty_list(self):
        action_type = ActionType.view
        record_id = 'dogma'

        expected_sessions = []

        sessions_that_seen = list(self.sut.get_sessions_that_seen_record(
            record_id=record_id, action_type=action_type))
        assert sorted(sessions_that_seen) == sorted(expected_sessions)
