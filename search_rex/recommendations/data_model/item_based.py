from .. import queries


class AbstractRecordBasedDataModel(object):
    """
    A wrapper around a concrete DataModel whose methods do not include
    the action_type and the include_internal_records as parameters
    """

    def get_records(self):
        '''Gets an iterator over all the records'''
        raise NotImplementedError()

    def get_seen_records(self, session_id):
        """
        Retrieves the records that the session interacted with
        """
        raise NotImplementedError()

    def get_sessions_that_seen_record(self, record_id):
        """
        Retrieves the session that interacted with the record
        """
        raise NotImplementedError()

    def get_record_columns(self):
        raise NotImplementedError()

    def get_preferences_of_session(self, session_id):
        """
        Retrieves the preferences that have been recorded in a session
        """
        raise NotImplementedError()

    def get_preferences_for_record(self, record_id):
        """
        Retrieves the preferences that have been recorded for a particular
        record
        """
        raise NotImplementedError()


class RecordBasedDataModel(AbstractRecordBasedDataModel):
    """
    A wrapper around a concrete DataModel whose methods do not include
    the action_type and the include_internal_records as parameters

    The action_type and the include_internal_records are passed in the ctor
    """

    def __init__(
            self, action_type, include_internal_records):
        self.action_type = action_type
        self.include_internal_records = include_internal_records

    def get_records(self):
        '''Gets an iterator over all the records'''
        return queries.get_records(self.include_internal_records)

    def get_seen_records(self, session_id):
        """
        Retrieves the records that the session interacted with
        """
        return queries.get_seen_records(session_id, self.action_type)

    def get_sessions_that_seen_record(self, record_id):
        """
        Retrieves the session that interacted with the record
        """
        return queries.get_sessions_that_used_record(
            record_id, self.action_type)

    def get_record_columns(self):

        return queries.get_record_columns(
            self.action_type, self.include_internal_records)


class InMemoryRecordBasedDataModel(AbstractRecordBasedDataModel):

    def __init__(self, data_model):
        self.data_model = data_model
        self.record_session_mat = {}
        self.init_model()

    def init_model(self):
        record_session_mat = {}

        for record_id, sessions in self.data_model.get_record_columns():
            record_session_mat[record_id] = sessions

        self.record_session_mat = record_session_mat

    def get_records(self):
        return self.record_session_mat.keys()

    def get_sessions_that_seen_record(self, record_id):
        if record_id not in self.record_session_mat:
            return []
        return self.record_session_mat[record_id]

    def get_seen_records(self, session_id):
        """
        Retrieves the records that the session interacted with
        """
        records = []
        for record_id, sessions in self.record_session_mat.iteritems():
            if session_id in sessions:
                records.append(record_id)
        return records

    def get_record_columns(self):
        for record_id, sessions in self.record_session_mat.iteritems():
            yield record_id, sessions
