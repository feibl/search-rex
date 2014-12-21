from test_base import BaseTestCase
from datetime import datetime
from search_rex.core import db
from search_rex.services import report_view_action
from search_rex.services import report_copy_action
from search_rex.services import set_record_active
from search_rex.services import RecordNotPresentException
from search_rex.models import Action
from search_rex.models import Record
from search_rex.models import ActionType
from search_rex.models import SearchQuery
from search_rex.models import SearchSession


class ReportActionTestCase(object):

    def test__report_action__view_created(self):
        query_string = 'abc'
        session_id = '1234'
        record_id = 'treehugging'
        timestamp = datetime(1999, 11, 11)
        is_internal_record = True

        self.report_action(
            record_id=record_id, is_internal_record=is_internal_record,
            session_id=session_id, query_string=query_string,
            timestamp=timestamp)

        assert Action.query.filter_by(
            query_string=query_string, session_id=session_id,
            record_id=record_id, time_created=timestamp,
            action_type=self.action_type
        ).one()

    def test__report_action__search_session_created(self):
        query_string = 'abc'
        session_id = '1234'
        record_id = 'treehugging'
        timestamp = datetime(1999, 11, 11)
        is_internal_record = True

        self.report_action(
            record_id=record_id, is_internal_record=is_internal_record,
            session_id=session_id, query_string=query_string,
            timestamp=timestamp)

        assert SearchSession.query.filter_by(
            session_id=session_id,
            time_created=timestamp).one()

    def test__report_action__active_record_created(self):
        query_string = 'abc'
        session_id = '1234'
        record_id = 'treehugging'
        timestamp = datetime(1999, 11, 11)
        is_internal_record = True

        self.report_action(
            record_id=record_id, is_internal_record=is_internal_record,
            session_id=session_id, query_string=query_string,
            timestamp=timestamp)

        assert Record.query.filter_by(
            record_id=record_id,
            is_internal=is_internal_record,
            active=True).one()

    def test__report_action_with_query_string__search_query_created(self):
        query_string = 'abc'
        session_id = '1234'
        record_id = 'treehugging'
        timestamp = datetime(1999, 11, 11)
        is_internal_record = True

        self.report_action(
            record_id=record_id, is_internal_record=is_internal_record,
            session_id=session_id, query_string=query_string,
            timestamp=timestamp)

        assert SearchQuery.query.filter_by(
            query_string=query_string).one()

    def test__report_action_with_no_query_string__no_search_query_created(self):
        session_id = '1234'
        record_id = 'treehugging'
        timestamp = datetime(1999, 11, 11)
        is_internal_record = True

        self.report_action(
            record_id=record_id, is_internal_record=is_internal_record,
            session_id=session_id, timestamp=timestamp)

        assert SearchQuery.query.filter().count() == 0
        assert Action.query.filter_by(
            query_string=None, session_id=session_id,
            record_id=record_id, time_created=timestamp,
            action_type=self.action_type
            ).one()

    def test__report_actions_on_different_records_from_same_session__two_actions_created(self):
        session_id = '1234'
        record_id_1 = 'treehugging'
        record_id_2 = 'streethugging'
        timestamp_1 = datetime(1999, 11, 11)
        timestamp_2 = datetime(1999, 11, 12)
        query_string = 'hugging'
        is_internal_record = True

        self.report_action(
            record_id=record_id_1, is_internal_record=is_internal_record,
            session_id=session_id, timestamp=timestamp_1,
            query_string=query_string)
        self.report_action(
            record_id=record_id_2, is_internal_record=is_internal_record,
            session_id=session_id, timestamp=timestamp_2,
            query_string=query_string)

        assert Action.query.filter().count() == 2
        assert Action.query.filter_by(
            query_string=query_string, session_id=session_id,
            record_id=record_id_1, time_created=timestamp_1,
            action_type=self.action_type
            ).one()
        assert Action.query.filter_by(
            query_string=query_string, session_id=session_id,
            record_id=record_id_2, time_created=timestamp_2,
            action_type=self.action_type
            ).one()

    def test__report_actions_on_same_record_from_same_session_with_same_query__no_new_action_created(self):
        query_string = 'abc'
        session_id = '1234'
        record_id = 'treehugging'
        timestamp_1 = datetime(1999, 11, 11)
        timestamp_2 = datetime(1999, 11, 12)
        is_internal_record = True

        self.report_action(
            record_id=record_id, is_internal_record=is_internal_record,
            session_id=session_id, query_string=query_string,
            timestamp=timestamp_1)
        self.report_action(
            record_id=record_id, is_internal_record=is_internal_record,
            session_id=session_id, query_string=query_string,
            timestamp=timestamp_2)

        assert Action.query.filter().count() == 1
        assert Action.query.filter_by(
            session_id=session_id, record_id=record_id,
            time_created=timestamp_2, action_type=self.action_type,
            query_string=query_string
            ).count() == 0

    def test__report_actions_on_same_record_from_same_session_with_different_query__no_new_action_created(self):
        query_string_1 = 'abc'
        query_string_2 = 'hug'
        session_id = '1234'
        record_id = 'treehugging'
        timestamp_1 = datetime(1999, 11, 11)
        timestamp_2 = datetime(1999, 11, 12)
        is_internal_record = True

        self.report_action(
            record_id=record_id, is_internal_record=is_internal_record,
            session_id=session_id, query_string=query_string_1,
            timestamp=timestamp_1)
        self.report_action(
            record_id=record_id, is_internal_record=is_internal_record,
            session_id=session_id, query_string=query_string_2,
            timestamp=timestamp_2)

        assert Action.query.filter().count() == 1
        assert Action.query.filter_by(
            session_id=session_id, record_id=record_id,
            time_created=timestamp_2, action_type=self.action_type,
            query_string=query_string_1
            ).count() == 0

    def test__report_actions_from_different_sessions(self):
        query_string = 'abc'
        session_id_1 = '1234'
        session_id_2 = '556'
        record_id = 'treehugging'
        timestamp = datetime(1999, 11, 11)
        is_internal_record = True

        self.report_action(
            record_id=record_id, is_internal_record=is_internal_record,
            session_id=session_id_1, query_string=query_string,
            timestamp=timestamp)
        self.report_action(
            record_id=record_id, is_internal_record=is_internal_record,
            session_id=session_id_2, query_string=query_string,
            timestamp=timestamp)

        assert Action.query.filter().count() == 2
        assert Action.query.filter_by(
            session_id=session_id_1, record_id=record_id,
            time_created=timestamp, action_type=self.action_type,
            query_string=query_string
            ).one()
        assert Action.query.filter_by(
            session_id=session_id_2, record_id=record_id,
            time_created=timestamp, action_type=self.action_type,
            query_string=query_string
            ).one()


class ReportViewTestCase(BaseTestCase, ReportActionTestCase):

    action_type = ActionType.view

    def setUp(self):
        super(ReportViewTestCase, self).setUp()

    def report_action(
            self, record_id, is_internal_record, session_id,
            timestamp, query_string = None):
        return report_view_action(
            record_id=record_id, is_internal_record=is_internal_record,
            session_id=session_id, query_string=query_string,
            timestamp=timestamp)


class ReportCopyTestCase(BaseTestCase, ReportActionTestCase):

    action_type = ActionType.copy

    def setUp(self):
        super(ReportCopyTestCase, self).setUp()

    def report_action(
            self, record_id, is_internal_record, session_id,
            timestamp, query_string = None):
        return report_copy_action(
            record_id=record_id, is_internal_record=is_internal_record,
            session_id=session_id, query_string=query_string,
            timestamp=timestamp)


class ReportDifferentActionsTestCase(BaseTestCase):

    def setUp(self):
        super(ReportDifferentActionsTestCase, self).setUp()

    def test__copy_after_view_action__both_actions_created(self):
        query_string = 'abc'
        session_id = '1234'
        record_id = 'treehugging'
        timestamp_1 = datetime(1999, 11, 11)
        timestamp_2 = datetime(1999, 11, 12)
        is_internal_record = True

        report_view_action(
            record_id=record_id, is_internal_record=is_internal_record,
            session_id=session_id, query_string=query_string,
            timestamp=timestamp_1)
        report_copy_action(
            record_id=record_id, is_internal_record=is_internal_record,
            session_id=session_id, query_string=query_string,
            timestamp=timestamp_2)

        assert Action.query.filter().count() == 2
        assert Action.query.filter_by(
            session_id=session_id, record_id=record_id,
            time_created=timestamp_1, action_type=ActionType.view,
            query_string=query_string
            ).one()
        assert Action.query.filter_by(
            session_id=session_id, record_id=record_id,
            time_created=timestamp_2, action_type=ActionType.copy,
            query_string=query_string
            ).one()

    def test__view_after_copy_action__both_actions_created(self):
        query_string = 'abc'
        session_id = '1234'
        record_id = 'treehugging'
        timestamp_1 = datetime(1999, 11, 11)
        timestamp_2 = datetime(1999, 11, 12)
        is_internal_record = True

        report_copy_action(
            record_id=record_id, is_internal_record=is_internal_record,
            session_id=session_id, query_string=query_string,
            timestamp=timestamp_1)
        report_view_action(
            record_id=record_id, is_internal_record=is_internal_record,
            session_id=session_id, query_string=query_string,
            timestamp=timestamp_2)

        assert Action.query.filter().count() == 2
        assert Action.query.filter_by(
            session_id=session_id, record_id=record_id,
            time_created=timestamp_2, action_type=ActionType.view,
            query_string=query_string
            ).one()
        assert Action.query.filter_by(
            session_id=session_id, record_id=record_id,
            time_created=timestamp_1, action_type=ActionType.copy,
            query_string=query_string
            ).one()


class SetRecordActiveTestCase(BaseTestCase):

    def setUp(self):
        super(SetRecordActiveTestCase, self).setUp()

    def test__set_active_record_inactive(self):
        is_active = True
        set_active_to = False
        is_internal = False
        record_id = 'caesar'

        session = db.session

        record = Record()
        record.active = is_active
        record.is_internal = is_internal
        record.record_id = record_id

        session.add(record)
        session.commit()

        set_record_active(record_id, set_active_to)

        assert Record.query.filter_by(
            record_id=record_id,
            is_internal=is_internal,
            active=set_active_to).one()

    def test__set_active_record_active(self):
        is_active = True
        set_active_to = True
        is_internal = False
        record_id = 'caesar'

        session = db.session

        record = Record()
        record.active = is_active
        record.is_internal = is_internal
        record.record_id = record_id

        session.add(record)
        session.commit()

        set_record_active(record_id, set_active_to)

        assert Record.query.filter_by(
            record_id=record_id,
            is_internal=is_internal,
            active=set_active_to).one()

    def test__set_inactive_record_active(self):
        is_active = False
        set_active_to = True
        is_internal = False
        record_id = 'caesar'

        session = db.session

        record = Record()
        record.active = is_active
        record.is_internal = is_internal
        record.record_id = record_id

        session.add(record)
        session.commit()

        set_record_active(record_id, set_active_to)

        assert Record.query.filter_by(
            record_id=record_id,
            is_internal=is_internal,
            active=set_active_to).one()

    def test__set_inactive_record_inactive(self):
        is_active = False
        set_active_to = False
        is_internal = False
        record_id = 'caesar'

        session = db.session

        record = Record()
        record.active = is_active
        record.is_internal = is_internal
        record.record_id = record_id

        session.add(record)
        session.commit()

        set_record_active(record_id, set_active_to)

        assert Record.query.filter_by(
            record_id=record_id,
            is_internal=is_internal,
            active=set_active_to).one()

    def test__set_record_active__record_not_present__exception_thrown(self):
        is_active = False
        set_active_to = False
        is_internal = False
        record_id = 'caesar'

        exception_thrown = False
        try:
            set_record_active(record_id, set_active_to)
        except RecordNotPresentException:
            exception_thrown = True

        assert exception_thrown
