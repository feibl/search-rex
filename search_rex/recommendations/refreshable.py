from threading import RLock


class Refreshable(object):
    def refresh(self, refreshed_components):
        raise NotImplementedError()


class RefreshHelper(object):
    """
    Helper class for calling refresh

    Allows adding dependencies that are called before refreshing the target
    component. The target component can specify a function that is called after
    all dependencies are refreshed
    """

    def __init__(self, target_refresh_function=None):
        self.target_refresh_function = target_refresh_function
        self.dependencies = []
        self.reentrant_lock = RLock()

    def add_dependency(self, refreshable):
        assert isinstance(refreshable, Refreshable)
        self.dependencies.append(refreshable)

    def refresh(self, refreshed_components):
        with self.reentrant_lock:
            for dep in self.dependencies:
                if dep not in refreshed_components:
                    dep.refresh(refreshed_components)
                    refreshed_components.add(dep)
            if self.target_refresh_function:
                self.target_refresh_function()
