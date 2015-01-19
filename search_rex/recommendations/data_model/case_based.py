from .. import queries
from search_rex.models import ActionType


class AbstractQueryBasedDataModel(object):
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


class QueryBasedDataModel(AbstractQueryBasedDataModel):
    """
    A wrapper around a concrete DataModel whose methods do not include
    the action_type and the include_internal_records as parameters

    The action_type and the include_internal_records are passed in the ctor
    """

    def __init__(
            self, include_internal_records,
            half_life_in_days=150, life_span_in_days=300):
        self.action_type = ActionType.view
        self.include_internal_records = include_internal_records
        self.half_life_in_days = half_life_in_days
        self.life_span_in_days = life_span_in_days

    def get_queries(self):
        '''Gets an iterator over all the records'''
        return queries.get_queries()

    def get_hits_for_queries(self, query_strings):
        """
        Retrieves the hit rows of the given queries
        """
        return queries.get_hits_for_queries(
            query_strings, self.action_type, self.include_internal_records,
            self.half_life_in_days, self.life_span_in_days)
