from .. import queries
from ..refreshable import Refreshable
from ..refreshable import RefreshHelper
from search_rex.models import ActionType
from datetime import timedelta
from search_rex.util.math_util import exp_decay
from search_rex.util.date_util import utcnow


class Hit(object):

    def __init__(self, value, last_interaction):
        self.value = value
        self.last_interaction = last_interaction
        self.num_copies = 0
        self.num_views = 0


class AbstractQueryDataModel(Refreshable):
    """
    A wrapper around a concrete DataModel whose methods do not include
    the action_type and the include_internal_records as parameters
    """

    def get_queries(self):
        '''Gets an iterator over all the records'''
        raise NotImplementedError()

    def get_hits_for_queries(self, query_strings):
        """
        Retrieves the hit rows of the given queries
        """
        raise NotImplementedError()


class PersistentQueryDataModel(AbstractQueryDataModel):
    """
    A wrapper around a concrete DataModel whose methods do not include
    the action_type and the include_internal_records as parameters

    The action_type and the include_internal_records are passed in the ctor
    """

    def __init__(
            self, include_internal_records, copy_action_weight=2.0,
            view_action_weight=1.0, perform_time_decay=True,
            time_interval=timedelta(days=1), half_life=50, max_age=300):
        self.include_internal_records = include_internal_records
        self.view_action_weight = view_action_weight
        self.copy_action_weight = copy_action_weight
        self.perform_time_decay = perform_time_decay
        self.time_interval = time_interval
        self.half_life = half_life
        self.max_age = max_age

    def __get_hits_from_actions(self, actions):
        hits = {}
        for action in actions:
            record = action.record_id

            hit_value = 0.0
            if action.action_type == ActionType.view:
                hit_value = self.view_action_weight
            elif action.action_type == ActionType.copy:
                hit_value = self.copy_action_weight

            if self.perform_time_decay:
                hit_value = exp_decay(
                    hit_value, utcnow(), action.time_created,
                    self.time_interval, self.half_life, self.max_age)

            if record not in hits:
                hit = Hit(0.0, action.time_created)
                hits[record] = hit
            else:
                hit = hits[record]

            hit.value += hit_value
            if action.time_created > hit.last_interaction:
                hit.last_interaction = action.time_created
            if action.action_type == ActionType.view:
                hit.num_views += 1
            elif action.action_type == ActionType.copy:
                hit.num_copies += 1

        return hits

    def get_queries(self):
        '''Gets an iterator over all the records'''
        return queries.get_queries()

    def get_hit_rows_for_queries(self, target_queries):
        """
        Retrieves the hit rows of the given queries
        """
        for query, actions in queries.get_actions_for_queries(
                self.include_internal_records, target_queries):
            hits = self.__get_hits_from_actions(actions)
            yield (query, hits)

    def get_hit_rows(self):
        """
        Retrieves the hit rows of the given queries
        """
        for query, actions in queries.get_actions_for_queries(
                self.include_internal_records):
            hits = self.__get_hits_from_actions(actions)

            yield (query, hits)

    def refresh(self, refreshed_components):
        """
        Adds itself to the refreshed_components as it works directly on the
        database
        """
        refreshed_components.add(self)


class InMemoryQueryDataModel(AbstractQueryDataModel):

    def __init__(self, data_model):
        self.data_model = data_model
        self.hit_mat = {}
        self.refresh_helper = RefreshHelper(
            target_refresh_function=self.init_model)
        self.refresh_helper.add_dependency(data_model)
        self.init_model()

    def init_model(self):
        hit_mat = {}

        for query, hits in\
                self.data_model.get_hit_rows():
            hit_mat[query] = hits

        self.hit_mat = hit_mat

    def get_queries(self):
        """
        Gets an iterator over all the records
        """
        return self.hit_mat.keys()

    def get_hit_rows_for_queries(self, queries):
        """
        Retrieves the hit rows of the given queries
        """
        for query in queries:
            if query in self.hit_mat:
                yield(query, self.hit_mat[query])

    def get_hit_rows(self):
        """
        Retrieves the hit rows
        """
        for query, hits in self.hit_mat.iteritems():
            yield(query, hits)

    def refresh(self, refreshed_components):
        """
        No refresh needed as the class works directly on the database
        """
        self.refresh_helper.refresh(refreshed_components)
        refreshed_components.add(self)
