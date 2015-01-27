from datetime import datetime
from search_rex.services import set_record_active
from search_rex.services import report_action
from search_rex.models import ActionType
import os

_cwd = os.path.dirname(os.path.abspath(__file__))


session_alice = 'alice'
session_bob = 'bob'
session_carol = 'carol'
session_dave = 'dave'
session_eric = 'eric'
session_frank = 'frank'
session_garry = 'garry'
session_hally = 'hally'
session_ian = 'ian'
session_isolated = 'isolated'
session_seen_all = 'seen all'
session_seen_nothing = 'seen nothing'

query_caesar = 'Caesar'
query_julius = 'Julius Caesar'
query_caesar_secrets = 'Secrets of Caesar'
query_brutus = 'Brutus'
query_brutus_caesar = 'Brutus Caesar'
query_napoleon = 'Napoleon'

record_napoleon = 'napoleon'
record_caesar = 'caesar'
record_brutus = 'brutus'
record_caesar_secrets = 'secrets_of_caesar'
record_cleopatra = 'cleopatra'
record_inactive = 'inactive'

query_sims = {
    query_caesar: {
        query_caesar: 1.0,
        query_julius: 0.8,
        query_brutus_caesar: 0.5,
        query_caesar_secrets: 0.9,
    },
    query_brutus: {
        query_brutus: 1.0,
        query_brutus_caesar: 0.5,
    },
    query_julius: {
        query_julius: 1.0,
        query_caesar: 0.8,
        query_caesar_secrets: 0.7,
        query_brutus_caesar: 0.4,
    },
    query_caesar_secrets: {
        query_julius: 0.7,
        query_caesar: 0.9,
        query_caesar_secrets: 1.0,
        query_brutus_caesar: 0.2,
    },
    query_brutus_caesar: {
        query_julius: 0.4,
        query_caesar: 0.5,
        query_caesar_secrets: 0.2,
        query_brutus_caesar: 1.0,
        query_brutus: 0.5,
    },
    query_napoleon: {
        query_napoleon: 1.0,
    },
}

is_internal = {
    record_napoleon: False,
    record_caesar: False,
    record_brutus: False,
    record_cleopatra: False,
    record_inactive: False,
    record_caesar_secrets: True,
}

is_active = {
    record_napoleon: True,
    record_caesar: True,
    record_brutus: True,
    record_cleopatra: True,
    record_caesar_secrets: True,
    record_inactive: False,
}

#     ca, br, cl, na, sec


view_matrix = {
    query_caesar: {
        record_caesar: 2,
        record_brutus: 1,
        record_cleopatra: 1,
        record_caesar_secrets: 2,
        record_inactive: 1,
    },
    query_julius: {
        record_caesar: 1,
        record_caesar_secrets: 1,
        record_inactive: 1,
    },
    query_caesar_secrets: {
    },
    query_brutus: {
        record_caesar: 1,
        record_brutus: 3,
    },
    query_brutus_caesar: {
        record_brutus: 1,
        record_caesar: 2,
    },
    query_napoleon: {
        record_napoleon: 2
    },
}

copy_matrix = {
    query_caesar: {
        record_caesar: 1,
        record_caesar_secrets: 1,
    },
    query_julius: {
        record_caesar: 1,
    },
    query_caesar_secrets: {
        record_caesar_secrets: 2,
    },
    query_brutus: {
        record_brutus: 1,
    },
    query_brutus_caesar: {
    },
    query_napoleon: {
        record_napoleon: 1
    },
}


class SessionGenerator(object):
    """
    Small counter for generating sessions
    """
    def __init__(self):
        self.count = 0

    def get_next(self):
        session_id = self.count
        self.count += 1
        return session_id


def import_matrix(
        action_type, session_gen, matrix, timestamp=datetime.utcnow()):
    for query_string, records in matrix.iteritems():
        for record_id, num_uses in records.iteritems():
            for i in xrange(num_uses):
                report_action(
                    action_type=action_type,
                    record_id=record_id,
                    timestamp=timestamp,
                    session_id=session_gen.get_next(),
                    query_string=query_string,
                    is_internal_record=is_internal[record_id])


def import_test_data(views, copies, timestamp=datetime.utcnow()):
    session_gen = SessionGenerator()

    import_matrix(ActionType.view, session_gen, views, timestamp)
    import_matrix(ActionType.copy, session_gen, copies, timestamp)

    for record_id, active in is_active.iteritems():
        set_record_active(record_id=record_id, active=active)
