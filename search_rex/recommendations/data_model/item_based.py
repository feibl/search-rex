from .. import queries
from search_rex.models import ActionType


class Preference(object):
    def __init__(self, value, preference_time):
        self.value = value
        self.preference_time = preference_time


class AbstractRecordDataModel(object):
    """
    A wrapper around a concrete DataModel whose methods do not include
    the action_type and the include_internal_records as parameters
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
    A wrapper around a concrete DataModel whose methods do not include
    the action_type and the include_internal_records as parameters

    The action_type and the include_internal_records are passed in the ctor
    """

    def __init__(
            self, include_internal_records, copy_action_weight=2.0,
            view_action_weight=1.0):
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


class InMemoryRecordDataModel(AbstractRecordDataModel):

    def __init__(self, data_model):
        self.data_model = data_model
        self.record_session_mat = {}
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
        records = []
        for record_id, sessions in self.record_session_mat.iteritems():
            if session_id in sessions:
                records.append(record_id)
        return records

    def get_preferences_for_record(self, record_id):
        """
        Retrieves the preferences for the record
        """
        if record_id not in self.record_session_mat:
            return []
        return self.record_session_mat[record_id]

    def get_preferences_for_records(self):
        """
        Retrieves the preference columns of all records
        """
        for record_id, sessions in self.record_session_mat.iteritems():
            yield record_id, sessions
