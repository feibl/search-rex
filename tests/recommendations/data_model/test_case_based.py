from search_rex.recommendations.data_model.case_based import\
    PersistentQueryDataModel
from search_rex.recommendations.data_model.case_based import\
    AbstractQueryDataModel
from search_rex.recommendations.data_model.case_based import\
    InMemoryQueryDataModel
from search_rex.recommendations.data_model.case_based import\
    Hit
from search_rex.recommendations import queries
from datetime import datetime
from datetime import timedelta
from search_rex.models import Action
from search_rex.models import ActionType
import mock
from search_rex.util import date_util


def create_action(action_type, query_str, record_id, time_created):
    action = Action()
    action.action_type = action_type
    action.record_id = record_id
    action.time_created = time_created
    action.query_str = query_str
    return action


def assert_hit_equal(hit1, hit2):
    assert hit1.value == hit2.value
    assert hit1.last_interaction == hit2.last_interaction


def test__pers_dm__get_hit_rows__no_decay():
    record_caesar = 'caesar'
    record_brutus = 'brutus'
    query_rome = 'rome'
    rome_view_caesar = create_action(
        ActionType.view, query_rome, record_caesar, datetime(1999, 1, 1))
    rome_copy_caesar = create_action(
        ActionType.copy, query_rome, record_caesar, datetime(1999, 1, 2))
    rome_view_brutus = create_action(
        ActionType.view, query_rome, record_brutus, datetime(1999, 1, 3))

    queries.get_actions_for_queries = mock.Mock(
        return_value={
            query_rome: [rome_view_caesar, rome_copy_caesar, rome_view_brutus]
        }.iteritems())

    copy_weight = 2.0
    view_weight = 1.0
    expected_caesar_hit = Hit(
        3.0, rome_copy_caesar.time_created)
    expected_brutus_hit = Hit(
        1.0, rome_view_brutus.time_created)

    sut = PersistentQueryDataModel(
        include_internal_records=True, copy_action_weight=copy_weight,
        view_action_weight=view_weight, perform_time_decay=False)

    hits = list(sut.get_hit_rows())

    assert len(hits) == 1
    query, query_hits = hits[0]
    assert query == query_rome

    assert_hit_equal(query_hits[record_caesar], expected_caesar_hit)
    assert_hit_equal(query_hits[record_brutus], expected_brutus_hit)


def test__pers_dm__get_hit_rows__with_decay():
    record_caesar = 'caesar'
    record_brutus = 'brutus'
    query_rome = 'rome'
    rome_view_caesar = create_action(
        ActionType.view, query_rome, record_caesar, datetime(1999, 1, 3))
    rome_copy_caesar = create_action(
        ActionType.copy, query_rome, record_caesar, datetime(1999, 1, 4))
    rome_view_brutus = create_action(
        ActionType.view, query_rome, record_brutus, datetime(1999, 1, 4))

    queries.get_actions_for_queries = mock.Mock(
        return_value={
            query_rome: [rome_view_caesar, rome_copy_caesar, rome_view_brutus]
        }.iteritems())

    date_util._utcnow = mock.Mock(return_value=datetime(1999, 1, 4))

    copy_weight = 2.0
    view_weight = 1.0

    expected_caesar_hit = Hit(
        2.5, rome_copy_caesar.time_created)
    expected_brutus_hit = Hit(
        1.0, rome_view_brutus.time_created)

    sut = PersistentQueryDataModel(
        include_internal_records=True, copy_action_weight=copy_weight,
        view_action_weight=view_weight, perform_time_decay=True,
        time_interval=timedelta(days=1), half_life=1, max_age=4
    )

    hits = list(sut.get_hit_rows())

    assert len(hits) == 1
    query, query_hits = hits[0]
    assert query == query_rome

    assert_hit_equal(query_hits[record_caesar], expected_caesar_hit)
    assert_hit_equal(query_hits[record_brutus], expected_brutus_hit)


def test__pers_dm__get_hit_rows_for_queries__no_decay():
    record_caesar = 'caesar'
    record_brutus = 'brutus'
    query_rome = 'rome'
    rome_view_caesar = create_action(
        ActionType.view, query_rome, record_caesar, datetime(1999, 1, 1))
    rome_copy_caesar = create_action(
        ActionType.copy, query_rome, record_caesar, datetime(1999, 1, 2))
    rome_view_brutus = create_action(
        ActionType.view, query_rome, record_brutus, datetime(1999, 1, 3))

    queries.get_actions_for_queries = mock.Mock(
        return_value={
            query_rome: [rome_view_caesar, rome_copy_caesar, rome_view_brutus]
        }.iteritems())

    copy_weight = 2.0
    view_weight = 1.0
    expected_caesar_hit = Hit(
        3.0, rome_copy_caesar.time_created)
    expected_brutus_hit = Hit(
        1.0, rome_view_brutus.time_created)

    sut = PersistentQueryDataModel(
        include_internal_records=True, copy_action_weight=copy_weight,
        view_action_weight=view_weight, perform_time_decay=False)

    hits = list(sut.get_hit_rows_for_queries([query_rome]))

    assert len(hits) == 1
    query, query_hits = hits[0]
    assert query == query_rome

    assert_hit_equal(query_hits[record_caesar], expected_caesar_hit)
    assert_hit_equal(query_hits[record_brutus], expected_brutus_hit)


def test__pers_dm__get_hit_rows_for_queries__with_decay():
    record_caesar = 'caesar'
    record_brutus = 'brutus'
    query_rome = 'rome'
    rome_view_caesar = create_action(
        ActionType.view, query_rome, record_caesar, datetime(1999, 1, 3))
    rome_copy_caesar = create_action(
        ActionType.copy, query_rome, record_caesar, datetime(1999, 1, 4))
    rome_view_brutus = create_action(
        ActionType.view, query_rome, record_brutus, datetime(1999, 1, 4))

    queries.get_actions_for_queries = mock.Mock(
        return_value={
            query_rome: [rome_view_caesar, rome_copy_caesar, rome_view_brutus]
        }.iteritems())

    date_util._utcnow = mock.Mock(return_value=datetime(1999, 1, 4))

    copy_weight = 2.0
    view_weight = 1.0

    expected_caesar_hit = Hit(
        2.5, rome_copy_caesar.time_created)
    expected_brutus_hit = Hit(
        1.0, rome_view_brutus.time_created)

    sut = PersistentQueryDataModel(
        include_internal_records=True, copy_action_weight=copy_weight,
        view_action_weight=view_weight, perform_time_decay=True,
        time_interval=timedelta(days=1), half_life=1, max_age=4
    )

    hits = list(sut.get_hit_rows_for_queries([query_rome]))

    assert len(hits) == 1
    query, query_hits = hits[0]
    assert query == query_rome

    assert_hit_equal(query_hits[record_caesar], expected_caesar_hit)
    assert_hit_equal(query_hits[record_brutus], expected_brutus_hit)


def test__pers_dm__refresh():
    sut = PersistentQueryDataModel(include_internal_records=True)

    refreshed_components = set()
    sut.refresh(refreshed_components)

    assert sut in refreshed_components


def test__in_mem_dm__get_hit_rows():
    query_rome = 'rome'
    query_caesar = 'caesar'

    record_brutus = 'brutus'
    record_caesar = 'caesar'

    hits = {
        query_rome: {
            record_caesar: Hit(1.0, datetime(1999, 1, 1)),
            record_brutus: Hit(2.0, datetime(1999, 1, 1)),
        },
        query_caesar: {
            record_caesar: Hit(1.0, datetime(1999, 1, 1)),
        }
    }
    fake_model = AbstractQueryDataModel()
    fake_model.get_hit_rows = mock.Mock(
        return_value=hits.iteritems())

    sut = InMemoryQueryDataModel(fake_model)

    for query, q_hits in sut.get_hit_rows():
        for record, hit in q_hits.iteritems():
            assert hits[query][record] == hit


def test__in_mem_dm__get_hit_rows_for_queries():
    query_rome = 'rome'
    query_caesar = 'caesar'

    record_brutus = 'brutus'
    record_caesar = 'caesar'

    hits = {
        query_rome: {
            record_caesar: Hit(1.0, datetime(1999, 1, 1)),
            record_brutus: Hit(2.0, datetime(1999, 1, 1)),
        },
        query_caesar: {
            record_caesar: Hit(1.0, datetime(1999, 1, 1)),
        }
    }
    fake_model = AbstractQueryDataModel()
    fake_model.get_hit_rows = mock.Mock(
        return_value=hits.iteritems())

    sut = InMemoryQueryDataModel(fake_model)

    ret_hits = list(sut.get_hit_rows_for_queries([query_rome]))
    assert len(ret_hits) == 1

    query, q_hits = ret_hits[0]

    assert query == query_rome

    for record, hit in q_hits.iteritems():
        assert hits[query_rome][record] == hit


def test__in_mem_dm__get_hit_rows_for_queries__unknown_query():
    query_rome = 'rome'
    query_caesar = 'caesar'

    query_unknown = 'unknown'

    record_brutus = 'brutus'
    record_caesar = 'caesar'

    hits = {
        query_rome: {
            record_caesar: Hit(1.0, datetime(1999, 1, 1)),
            record_brutus: Hit(2.0, datetime(1999, 1, 1)),
        },
        query_caesar: {
            record_caesar: Hit(1.0, datetime(1999, 1, 1)),
        }
    }
    fake_model = AbstractQueryDataModel()
    fake_model.get_hit_rows = mock.Mock(
        return_value=hits.iteritems())

    sut = InMemoryQueryDataModel(fake_model)

    ret_hits = list(sut.get_hit_rows_for_queries([query_unknown]))
    assert len(ret_hits) == 0


def test__in_mem_dm__get_queries():
    query_rome = 'rome'
    query_caesar = 'caesar'

    record_brutus = 'brutus'
    record_caesar = 'caesar'

    hits = {
        query_rome: {
            record_caesar: Hit(1.0, datetime(1999, 1, 1)),
            record_brutus: Hit(2.0, datetime(1999, 1, 1)),
        },
        query_caesar: {
            record_caesar: Hit(1.0, datetime(1999, 1, 1)),
        }
    }
    fake_model = AbstractQueryDataModel()
    fake_model.get_hit_rows = mock.Mock(
        return_value=hits.iteritems())

    sut = InMemoryQueryDataModel(fake_model)

    ret_queries = list(sut.get_queries())
    assert sorted(hits.keys()) == sorted(ret_queries)


def test__in_mem_dm__refresh__underlying_data_model_is_refreshed():
    hits = {
    }
    fake_model = AbstractQueryDataModel()
    fake_model.get_hit_rows = mock.Mock(
        return_value=hits.iteritems())
    fake_model.refresh = mock.Mock()

    sut = InMemoryQueryDataModel(fake_model)

    refreshed_components = set()
    sut.refresh(refreshed_components)

    fake_model.refresh.assert_called_once_with(refreshed_components)
    assert fake_model in refreshed_components
    assert sut in refreshed_components


def test__in_mem_dm__refresh__data_is_reloaded():
    query_rome = 'rome'
    record_caesar = 'caesar'

    hits = {}
    fake_model = AbstractQueryDataModel()
    fake_model.get_hit_rows = mock.Mock(
        return_value=hits.iteritems())
    fake_model.refresh = mock.Mock()

    sut = InMemoryQueryDataModel(fake_model)

    assert {k: v for k, v in sut.get_hit_rows()} == {}

    hits[query_rome] = {
        record_caesar: Hit(1.0, datetime(1999, 1, 1)),
    }

    sut.refresh(set())

    for record_id, rec_prefs in sut.get_hit_rows():
        for session_id, pref in rec_prefs.iteritems():
            assert hits[record_id][session_id] == pref
