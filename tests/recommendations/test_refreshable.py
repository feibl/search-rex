import mock
from search_rex.recommendations.refreshable import RefreshHelper
from search_rex.recommendations.refreshable import Refreshable


def test__refresh__dependencies_refresh_is_called():
    refreshable1 = Refreshable()
    refreshable2 = Refreshable()

    refreshable1.refresh = mock.Mock()
    refreshable2.refresh = mock.Mock()

    sut = RefreshHelper()
    sut.add_dependency(refreshable1)
    sut.add_dependency(refreshable2)

    refreshed_components = set()
    sut.refresh(refreshed_components)

    assert refreshable1.refresh.call_count == 1
    assert refreshable2.refresh.call_count == 1


def test__refresh__refreshed_dependencies_are_not_called():
    refreshable1 = Refreshable()
    refreshable2 = Refreshable()

    refreshable1.refresh = mock.Mock()
    refreshable2.refresh = mock.Mock()

    sut = RefreshHelper()
    sut.add_dependency(refreshable1)
    sut.add_dependency(refreshable2)

    refreshed_components = set([refreshable1])
    sut.refresh(refreshed_components)

    assert refreshable1.refresh.call_count == 0


def test__refresh__refreshed_dependencies_are_added_to_refreshed_components():
    refreshable1 = Refreshable()
    refreshable2 = Refreshable()

    refreshable1.refresh = mock.Mock()
    refreshable2.refresh = mock.Mock()

    sut = RefreshHelper()
    sut.add_dependency(refreshable1)
    sut.add_dependency(refreshable2)

    refreshed_components = set()
    sut.refresh(refreshed_components)

    assert refreshed_components == set([refreshable1, refreshable2])
