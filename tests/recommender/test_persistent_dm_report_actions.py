from ..test_base import BaseTestCase
from search_rex.recommender.data_model import PersistentDataModel
from datetime import datetime
from search_rex.recommender.models import Action
from search_rex.recommender.models import Record
from search_rex.recommender.models import ActionType
from search_rex.recommender.models import SearchQuery
from search_rex.recommender.models import SearchSession


class ReportViewTestCase(BaseTestCase):

    def setUp(self):
        super(ReportViewTestCase, self).setUp()

        self.data_model = PersistentDataModel(
            action_type=ActionType.view,
            include_internal_records=True)

        self.session_id = '1234'
        self.record_id = 'treehugging'
        self.timestamp = datetime(1999, 11, 11)

    def report_action(
            self, query_string=None,
            record_id=None, is_internal_record=True,
            timestamp=None, session_id=None):
        timestamp = timestamp if timestamp else self.timestamp
        record_id = record_id if record_id else self.record_id
        session_id = session_id if session_id else self.session_id

        self.data_model.report_action(
            query_string=query_string,
            record_id=record_id, is_internal_record=is_internal_record,
            timestamp=timestamp, session_id=session_id)

    def test__view_created(self):
        query_string = 'abc'
        self.report_action(query_string=query_string)
        assert Action.query.filter_by(
            query_string=query_string, session_id=self.session_id,
            record_id=self.record_id, time_created=self.timestamp,
            action_type=ActionType.view
            ).one()

    def test__no_query_string__view_created(self):
        query_string = None
        self.report_action(query_string=query_string)
        assert Action.query.filter_by(
            query_string=query_string, session_id=self.session_id,
            record_id=self.record_id, time_created=self.timestamp,
            action_type=ActionType.view
            ).one()

    def test__duplicate_action__no_new_action_created(self):
        timestamp = datetime(2003, 11, 11)
        self.report_action()
        self.report_action(timestamp=timestamp)
        assert Action.query.filter_by(
            session_id=self.session_id,
            record_id=self.record_id, time_created=timestamp,
            action_type=ActionType.view
            ).count() == 0

    def test__search_query_created(self):
        query_string = 'abc'
        self.report_action(query_string=query_string)
        assert SearchQuery.query.filter_by(
            query_string=query_string).one()

    def test__no_query_string__no_search_query_created(self):
        query_string = 'abc'
        self.report_action(query_string=query_string)
        assert SearchQuery.query.filter_by().count()

    def test__search_session_created(self):
        self.report_action()
        assert SearchSession.query.filter_by(
            session_id=self.session_id,
            time_created=self.timestamp).one()

    def test__duplicate_action__no_new_search_session_created(self):
        timestamp = datetime(2003, 11, 11)
        self.report_action()
        self.report_action(timestamp=timestamp)
        assert SearchSession.query.filter_by(
            session_id=self.session_id,
            time_created=timestamp).count() == 0

    def test__record_created(self):
        record_id = 'Hahaha'
        is_internal_record = False
        self.report_action(
            record_id=record_id, is_internal_record=is_internal_record)
        assert Record.query.filter_by(
            record_id=record_id,
            is_internal=is_internal_record).one()


class ReportCopyTestCase(BaseTestCase):

    def setUp(self):
        super(ReportCopyTestCase, self).setUp()

        self.data_model = PersistentDataModel(
            action_type=ActionType.copy,
            include_internal_records=True)

        self.session_id = '1234'
        self.record_id = 'treehugging'
        self.timestamp = datetime(1999, 11, 11)

    def report_action(
            self, query_string=None,
            record_id=None, is_internal_record=True,
            timestamp=None, session_id=None):
        timestamp = timestamp if timestamp else self.timestamp
        record_id = record_id if record_id else self.record_id
        session_id = session_id if session_id else self.session_id

        self.data_model.report_action(
            query_string=query_string,
            record_id=record_id, is_internal_record=is_internal_record,
            timestamp=timestamp, session_id=session_id)

    def test__copy_created(self):
        query_string = 'abc'
        self.report_action(query_string=query_string)
        assert Action.query.filter_by(
            query_string=query_string, session_id=self.session_id,
            record_id=self.record_id, time_created=self.timestamp,
            action_type=ActionType.copy
            ).one()

    def test__no_query_string__copy_created(self):
        query_string = None
        self.report_action(query_string=query_string)
        assert Action.query.filter_by(
            query_string=query_string, session_id=self.session_id,
            record_id=self.record_id, time_created=self.timestamp,
            action_type=ActionType.copy
            ).one()

    def test__duplicate_action__no_new_action_created(self):
        timestamp = datetime(2003, 11, 11)
        self.report_action()
        self.report_action(timestamp=timestamp)
        assert Action.query.filter_by(
            session_id=self.session_id,
            record_id=self.record_id, time_created=timestamp,
            action_type=ActionType.copy
            ).count() == 0

    def test__search_query_created(self):
        query_string = 'abc'
        self.report_action(query_string=query_string)
        assert SearchQuery.query.filter_by(
            query_string=query_string).one()

    def test__no_query_string__no_search_query_created(self):
        query_string = 'abc'
        self.report_action(query_string=query_string)
        assert SearchQuery.query.filter_by().count()

    def test__search_session_created(self):
        self.report_action()
        assert SearchSession.query.filter_by(
            session_id=self.session_id,
            time_created=self.timestamp).one()

    def test__duplicate_action__no_new_search_session_created(self):
        timestamp = datetime(2003, 11, 11)
        self.report_action()
        self.report_action(timestamp=timestamp)
        assert SearchSession.query.filter_by(
            session_id=self.session_id,
            time_created=timestamp).count() == 0

    def test__record_created(self):
        record_id = 'Hahaha'
        is_internal_record = False
        self.report_action(
            record_id=record_id, is_internal_record=is_internal_record)
        assert Record.query.filter_by(
            record_id=record_id,
            is_internal=is_internal_record).one()
