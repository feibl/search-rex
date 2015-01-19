from datetime import datetime
from search_rex.services import set_record_active
from search_rex.services import report_view_action
from search_rex.services import report_copy_action
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

record_welcome = 'welcome'
record_napoleon = 'napoleon'
record_caesar = 'caesar'
record_brutus = 'brutus'
record_secrets_of_rome = 'secrets_of_rome'
record_cleopatra = 'cleopatra'
record_inactive = 'inactive'
record_isolated = 'isolated'

is_internal = {
    record_welcome: False,
    record_napoleon: False,
    record_caesar: False,
    record_brutus: False,
    record_cleopatra: False,
    record_inactive: False,
    record_isolated: False,
    record_secrets_of_rome: True,
}

is_active = {
    record_welcome: True,
    record_napoleon: True,
    record_caesar: True,
    record_brutus: True,
    record_secrets_of_rome: True,
    record_cleopatra: True,
    record_isolated: True,
    record_inactive: False,
}

view_actions = {
    session_alice: [
        record_welcome, record_caesar, record_brutus, record_inactive],
    session_bob: [
        record_welcome, record_caesar, record_brutus, record_cleopatra],
    session_carol: [
        record_welcome, record_cleopatra],
    session_dave: [
        record_welcome, record_caesar, record_secrets_of_rome],
    session_eric: [
        record_welcome, record_napoleon],
    session_frank: [
        record_welcome, record_caesar, record_brutus],
    session_garry: [
        record_welcome, record_caesar, record_cleopatra],
    session_hally: [
        record_welcome, record_brutus],
    session_ian: [
        record_welcome, record_secrets_of_rome],
    session_seen_all: [
        record_welcome, record_caesar, record_cleopatra, record_brutus,
        record_napoleon, record_secrets_of_rome, record_inactive],
    session_seen_nothing: [
        ],
    session_isolated: [
        record_isolated],
}

copy_actions = view_actions


def import_test_data(views, copies):
    for session_id, viewed_records in views.iteritems():
        for record_id in viewed_records:
            report_view_action(
                record_id=record_id,
                timestamp=datetime(1999, 1, 1),
                session_id=session_id,
                is_internal_record=is_internal[record_id])

    for session_id, copied_records in copies.iteritems():
        for record_id in copied_records:
            report_copy_action(
                record_id=record_id,
                timestamp=datetime(1999, 1, 1),
                session_id=session_id,
                is_internal_record=is_internal[record_id])

    for record_id, active in is_active.iteritems():
        set_record_active(record_id=record_id, active=active)
