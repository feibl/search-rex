from search_rex.recommendations.data_model.item_based import Preference
from search_rex.recommendations.data_model.item_based import\
    PersistentRecordDataModel
from search_rex.recommendations.data_model.item_based import\
    AbstractRecordDataModel
from search_rex.recommendations.data_model.item_based import\
    InMemoryRecordDataModel
from search_rex.recommendations import queries
from datetime import datetime
from search_rex.models import Action
from search_rex.models import ActionType
import mock


def test__preference__init():
    value = 1.0
    pref_time = datetime(1999, 12, 3)
    preference = Preference(value, pref_time)
    assert preference.value == value
    assert preference.preference_time == pref_time


session_alice = 'alice'
session_bob = 'bob'

record_caesar = 'caesar'
record_brutus = 'brutus'


def create_action(action_type, session_id, record_id, time_created):
    action = Action()
    action.session_id = session_id
    action.action_type = action_type
    action.record_id = record_id
    action.time_created = time_created
    return action


def assert_pref_equal(pref1, pref2):
    assert pref1.value == pref2.value
    assert pref1.preference_time == pref2.preference_time


def test__pers_dm__get_preferences_of_session__weights_are_set():
    alice_views_caesar = create_action(
        ActionType.view, session_alice, record_caesar, datetime(1999, 1, 1))
    alice_copies_caesar = create_action(
        ActionType.copy, session_alice, record_caesar, datetime(1999, 1, 2))
    alice_views_brutus = create_action(
        ActionType.view, session_alice, record_brutus, datetime(1999, 1, 3))

    queries.get_actions_of_session = mock.Mock(
        return_value=[
            alice_views_caesar, alice_copies_caesar, alice_views_brutus
        ])

    copy_weight = 2.0
    view_weight = 1.0
    expected_caesar_pref = Preference(
        copy_weight, alice_copies_caesar.time_created)
    expected_brutus_pref = Preference(
        view_weight, alice_views_brutus.time_created)

    sut = PersistentRecordDataModel(
        include_internal_records=True, copy_action_weight=copy_weight,
        view_action_weight=view_weight)

    prefs = sut.get_preferences_of_session(session_alice)

    assert len(prefs) == 2

    assert_pref_equal(prefs[record_caesar], expected_caesar_pref)
    assert_pref_equal(prefs[record_brutus], expected_brutus_pref)


def test__pers_dm__get_preferences_of_session__unknown_session():
    queries.get_actions_of_session = mock.Mock(return_value=[])
    sut = PersistentRecordDataModel(include_internal_records=True)

    prefs = sut.get_preferences_of_session('nobody')

    assert prefs == {}


def test__pers_dm__get_preferences_for_record__weights_are_set():
    alice_views_caesar = create_action(
        ActionType.view, session_alice, record_caesar, datetime(1999, 1, 1))
    alice_copies_caesar = create_action(
        ActionType.copy, session_alice, record_caesar, datetime(1999, 1, 2))
    bob_views_caesar = create_action(
        ActionType.view, session_bob, record_caesar, datetime(1999, 1, 3))

    queries.get_actions_on_record = mock.Mock(
        return_value=[
            alice_views_caesar, alice_copies_caesar, bob_views_caesar
        ])

    copy_weight = 2.0
    view_weight = 1.0
    expected_alice_pref = Preference(
        copy_weight, alice_copies_caesar.time_created)
    expected_bob_pref = Preference(
        view_weight, bob_views_caesar.time_created)

    sut = PersistentRecordDataModel(
        include_internal_records=True, copy_action_weight=copy_weight,
        view_action_weight=view_weight)

    prefs = sut.get_preferences_for_record(record_caesar)

    assert len(prefs) == 2

    assert_pref_equal(prefs[session_alice], expected_alice_pref)
    assert_pref_equal(prefs[session_bob], expected_bob_pref)


def test__pers_dm__get_preferences_for_record__unknown_record():
    queries.get_actions_on_record = mock.Mock(return_value=[])
    sut = PersistentRecordDataModel(include_internal_records=True)

    prefs = sut.get_preferences_for_record('random_page')

    assert prefs == {}


def test__pers_dm__get_preferences_for_records__weights_are_set():
    alice_views_caesar = create_action(
        ActionType.view, session_alice, record_caesar, datetime(1999, 1, 1))
    alice_copies_caesar = create_action(
        ActionType.copy, session_alice, record_caesar, datetime(1999, 1, 2))
    bob_views_caesar = create_action(
        ActionType.view, session_bob, record_caesar, datetime(1999, 1, 3))

    queries.get_actions_on_records = mock.Mock(
        return_value=[
            (
                record_caesar, [
                    alice_views_caesar, alice_copies_caesar, bob_views_caesar
                ]
            ),
        ])

    copy_weight = 2.0
    view_weight = 1.0
    expected_alice_pref = Preference(
        copy_weight, alice_copies_caesar.time_created)
    expected_bob_pref = Preference(
        view_weight, bob_views_caesar.time_created)

    sut = PersistentRecordDataModel(
        include_internal_records=True, copy_action_weight=copy_weight,
        view_action_weight=view_weight)

    returned_preferences = list(sut.get_preferences_for_records())

    assert len(returned_preferences) == 1
    record, prefs = returned_preferences[0]
    assert record == record_caesar
    assert len(prefs) == 2

    assert_pref_equal(prefs[session_alice], expected_alice_pref)
    assert_pref_equal(prefs[session_bob], expected_bob_pref)


def test__pers_dm__get_preferences_for_records__preferences_for_each_record():
    alice_views_caesar = create_action(
        ActionType.view, session_alice, record_caesar, datetime(1999, 1, 1))
    alice_copies_caesar = create_action(
        ActionType.copy, session_alice, record_caesar, datetime(1999, 1, 2))
    bob_views_caesar = create_action(
        ActionType.view, session_bob, record_caesar, datetime(1999, 1, 3))
    bob_views_brutus = create_action(
        ActionType.view, session_bob, record_brutus, datetime(1999, 1, 3))

    queries.get_actions_on_records = mock.Mock(
        return_value=[
            (
                record_caesar, [
                    alice_views_caesar, alice_copies_caesar, bob_views_caesar
                ],
            ),
            (
                record_brutus, [
                    bob_views_brutus,
                ]
            ),
        ])

    sut = PersistentRecordDataModel(
        include_internal_records=True)

    returned_preferences = list(sut.get_preferences_for_records())

    assert len(returned_preferences) == 2
    assert any(filter(lambda (r, _): r == record_caesar, returned_preferences))
    assert any(filter(lambda (r, _): r == record_brutus, returned_preferences))


def test__in_mem_dm__get_preferences_for_records():
    preferences = {
        record_caesar: {
            session_alice: Preference(1.0, datetime(1999, 1, 1)),
            session_bob: Preference(2.0, datetime(1999, 1, 1)),
        },
        record_brutus: {
            session_alice: Preference(1.0, datetime(1999, 1, 1)),
        }
    }
    fake_model = AbstractRecordDataModel()
    fake_model.get_preferences_for_records = mock.Mock(
        return_value=preferences.iteritems())

    sut = InMemoryRecordDataModel(fake_model)

    for record_id, rec_prefs in sut.get_preferences_for_records():
        for session_id, pref in rec_prefs.iteritems():
            assert preferences[record_id][session_id] == pref


def test__in_mem_dm__get_preferences_for_record():
    preferences = {
        record_caesar: {
            session_alice: Preference(1.0, datetime(1999, 1, 1)),
            session_bob: Preference(2.0, datetime(1999, 1, 1)),
        },
        record_brutus: {
            session_alice: Preference(1.0, datetime(1999, 1, 1)),
        }
    }
    fake_model = AbstractRecordDataModel()
    fake_model.get_preferences_for_records = mock.Mock(
        return_value=preferences.iteritems())

    sut = InMemoryRecordDataModel(fake_model)

    rec_prefs = sut.get_preferences_for_record(record_caesar)
    for session_id, pref in rec_prefs.iteritems():
        assert preferences[record_caesar][session_id] == pref


def test__in_mem_dm__get_preferences_for_record__record_not_present():
    preferences = {
        record_caesar: {
            session_alice: Preference(1.0, datetime(1999, 1, 1)),
            session_bob: Preference(2.0, datetime(1999, 1, 1)),
        },
        record_brutus: {
            session_alice: Preference(1.0, datetime(1999, 1, 1)),
        }
    }
    fake_model = AbstractRecordDataModel()
    fake_model.get_preferences_for_records = mock.Mock(
        return_value=preferences.iteritems())

    sut = InMemoryRecordDataModel(fake_model)

    assert sut.get_preferences_for_record('dogma') == {}


def test__in_mem_dm__get_preferences_of_session():
    preferences = {
        record_caesar: {
            session_alice: Preference(1.0, datetime(1999, 1, 1)),
            session_bob: Preference(2.0, datetime(1999, 1, 1)),
        },
        record_brutus: {
            session_alice: Preference(1.0, datetime(1999, 1, 1)),
        }
    }
    fake_model = AbstractRecordDataModel()
    fake_model.get_preferences_for_records = mock.Mock(
        return_value=preferences.iteritems())

    sut = InMemoryRecordDataModel(fake_model)

    sess_prefs = sut.get_preferences_of_session(session_alice)
    for record_id, pref in sess_prefs.iteritems():
        assert preferences[record_id][session_alice] == pref


def test__in_mem_dm__get_preferences_of_session__session_not_present():
    preferences = {
        record_caesar: {
            session_alice: Preference(1.0, datetime(1999, 1, 1)),
            session_bob: Preference(2.0, datetime(1999, 1, 1)),
        },
        record_brutus: {
            session_alice: Preference(1.0, datetime(1999, 1, 1)),
        }
    }
    fake_model = AbstractRecordDataModel()
    fake_model.get_preferences_for_records = mock.Mock(
        return_value=preferences.iteritems())

    sut = InMemoryRecordDataModel(fake_model)

    assert sut.get_preferences_of_session('dogma') == {}
