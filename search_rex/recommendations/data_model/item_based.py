"""
In this module, the similarity classes of the item-based approach are defined.
The most important classes are the CombinedRecordSimilarity, the
CollaborativeRecordSimilarity and the ContentRecordSimilarity. The first one
combines the record similarity values of two underlying item based similarity
classes. The second similarity class calculates the similarity of two records
by using a similarity metric, e.g., cosine similarity, on their preference
vectors. Finally, ContentRecordSimilarity retrieves the imported content-based
similarity from the database and stores in the local memory.
"""

from .. import queries
from search_rex.models import ActionType
from ..refreshable import Refreshable
from ..refreshable import RefreshHelper


class Preference(object):
    """
    An entry of the session-record matrix consisting of a value and a
    preference time
    """
    def __init__(self, value, preference_time):
        """
        :param value: the value of the preference
        :param preference_time: the time at which the preference was committed
        """
        self.value = value
        self.preference_time = preference_time


class AbstractRecordDataModel(Refreshable):
    """
    The repository for the session-record matrix
    """

    def get_records(self):
        """
        Gets an iterator over all the records
        """
        raise NotImplementedError()

    def get_preferences_of_session(self, session_id):
        """
        Retrieves the preferences of the session
        """
        raise NotImplementedError()

    def get_preferences_for_record(self, record_id):
        """
        Retrieves the preferences for the record
        """
        raise NotImplementedError()

    def get_preferences_for_records(self):
        """
        Retrieves the preference columns of all records
        """
        raise NotImplementedError()


class PersistentRecordDataModel(AbstractRecordDataModel):
    """
    This repository works directly on the database. It includes the variable
    include_internal_records that indicates if this repository includes
    internal records
    """

    def __init__(
            self, include_internal_records, copy_action_weight=2.0,
            view_action_weight=1.0):
        """
        :param include_internal_records: indicates if this repository includes
        internal records
        :param copy_action_weight: the preference value of a copy action
        :param view_action_weight: the preference value of a view action
        """
        self.include_internal_records = include_internal_records
        self.view_action_weight = view_action_weight
        self.copy_action_weight = copy_action_weight

    def get_records(self):
        """
        Gets an iterator over all the records
        """
        return queries.get_records(self.include_internal_records)

    def __get_preferences_from_actions(self, actions, key_func):
        preferences = {}
        for action in actions:
            key = key_func(action)
            if key not in preferences:
                pref_value = 0.0
                if action.action_type == ActionType.view:
                    pref_value = self.view_action_weight
                elif action.action_type == ActionType.copy:
                    pref_value = self.copy_action_weight

                preferences[key] = Preference(
                    value=pref_value, preference_time=action.time_created)

            elif action.action_type == ActionType.copy:
                preferences[key].value = self.copy_action_weight
                preferences[key].preference_time = action.time_created

        return preferences

    def get_preferences_of_session(self, session_id):
        """
        Retrieves the preferences of the session
        """
        actions = queries.get_actions_of_session(session_id)
        preferences = self.__get_preferences_from_actions(
            actions, lambda action: action.record_id)

        return preferences

    def get_preferences_for_record(self, record_id):
        """
        Retrieves the preferences for the record
        """
        actions = queries.get_actions_on_record(record_id)
        preferences = self.__get_preferences_from_actions(
            actions, lambda action: action.session_id)

        return preferences

    def get_preferences_for_records(self):
        """
        Retrieves the preference columns of all records
        """
        for record_id, actions in queries.get_actions_on_records(
                self.include_internal_records):
            preferences = self.__get_preferences_from_actions(
                actions, lambda action: action.session_id)

            yield (record_id, preferences)

    def refresh(self, refreshed_components):
        """
        No refresh needed as the class works directly on the database
        """
        refreshed_components.add(self)


class InMemoryRecordDataModel(AbstractRecordDataModel):
    """
    This data model retrieves the data from an underlying data model and stores
    the data in a dictionary. Calling refresh, reloads the data
    """

    def __init__(self, data_model):
        self.data_model = data_model
        self.record_session_mat = {}
        self.refresh_helper = RefreshHelper(
            target_refresh_function=self.init_model)
        self.refresh_helper.add_dependency(data_model)
        self.init_model()

    def init_model(self):
        record_session_mat = {}

        for record_id, preferences in\
                self.data_model.get_preferences_for_records():
            record_session_mat[record_id] = preferences

        self.record_session_mat = record_session_mat

    def get_records(self):
        """
        Gets an iterator over all the records
        """
        return self.record_session_mat.keys()

    def get_preferences_of_session(self, session_id):
        """
        Retrieves the preferences of the session
        """
        preferences = {}
        for record_id, rec_prefs in self.record_session_mat.iteritems():
            if session_id in rec_prefs:
                preferences[record_id] = rec_prefs[session_id]
        return preferences

    def get_preferences_for_record(self, record_id):
        """
        Retrieves the preferences for the record
        """
        if record_id not in self.record_session_mat:
            return {}
        return self.record_session_mat[record_id]

    def get_preferences_for_records(self):
        """
        Retrieves the preference columns of all records
        """
        for record_id, preferences in self.record_session_mat.iteritems():
            yield record_id, preferences

    def refresh(self, refreshed_components):
        """
        No refresh needed as the class works directly on the database
        """
        self.refresh_helper.refresh(refreshed_components)
        refreshed_components.add(self)
