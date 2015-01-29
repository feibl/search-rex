"""
Some implementations of the recommender components have a copy of the data
that is stored in the database. In order to incorporate the newest changes
in this data, they must be told to reload it from from time to time. However,
a recommender system is built of many different components. For this reason,
the update call must propagated to all the components. In order to do that each
component implements the Refreshable interface which provides a function that
derived classes can implement in order to refresh themselves. This interface
is declared in the refreshable module.
"""

from threading import RLock


class Refreshable(object):
    """
    Specifies the refresh functions. Classes that implement the Refreshable
    interface define how they need to be refreshed
    """
    def refresh(self, refreshed_components):
        """
        The function for refreshing a component

        :param refreshed_components: the set of already refreshed components
        """
        raise NotImplementedError()


class RefreshHelper(object):
    """
    Helper class for calling refresh

    Allows adding dependencies that are called before refreshing the target
    component. The target component can specify a function that is called after
    all dependencies are refreshed
    """

    def __init__(self, target_refresh_function=None):
        """
        :param target_refresh_function: the function that is called after the
        dependencies have been refreshed
        """
        self.target_refresh_function = target_refresh_function
        self.dependencies = []
        self.reentrant_lock = RLock()

    def add_dependency(self, refreshable):
        """
        Adds a refreshable object to the dependencies
        """
        assert isinstance(refreshable, Refreshable)
        self.dependencies.append(refreshable)

    def refresh(self, refreshed_components):
        """
        Refreshes all dependencies if they have not been already refreshed.
        Finally the targets refresh function is called
        """
        with self.reentrant_lock:
            for dep in self.dependencies:
                if dep not in refreshed_components:
                    dep.refresh(refreshed_components)
                    refreshed_components.add(dep)
            if self.target_refresh_function:
                self.target_refresh_function()
