from ..test_base import BaseTestCase
from search_rex.core import db
from search_rex.recommender.data_model import PersistentDataModel
from search_rex.recommender.models import Community


TEST_COMMUNITY = 'test_community'


def assert_404(response):
    """
    Checks if a HTTP 404 returned
    """
    assert response.status_code == 404


class TestParameters(BaseTestCase):

    def create_community(self, community_id):
        test_community = Community()
        test_community.community_id = TEST_COMMUNITY
        session = db.session
        session.add(test_community)
        session.commit()

    def setUp(self):
        super(TestParameters, self).setUp()
        self.data_model = PersistentDataModel()
        self.create_community(TEST_COMMUNITY)


def create_throws_404_test(view_to_test, parameters):
    def do_test_expected(self):
        pms_to_use = {k: v for k, v in parameters.items()}
        pms_to_use['api_key'] = self.app.config['API_KEY']
        response = self.client.get(view_to_test, data=pms_to_use)
        assert_404(response)
    return do_test_expected


def create_required_pms_tests(view, req_parameters):
    for leave_out_parameter in req_parameters.keys():
        pms_to_use = {}
        for parameter in req_parameters.keys():
            if parameter == leave_out_parameter:
                continue
            pms_to_use[parameter] = req_parameters[parameter]

            test_method = create_throws_404_test('/view', pms_to_use)
            test_method.__name__ = 'test___{}_omitting_{}__throws_404'\
                .format(view, leave_out_parameter)
            setattr(TestParameters, test_method.__name__, test_method)


view_parameters = dict(
    community_id=TEST_COMMUNITY,
    record_id='Secret document',
    query_string='hello world',
    session_id=5556,
    timestamp=1234555,
)

recommend_parameters = dict(
    community_id=TEST_COMMUNITY,
    query_string='hello world',
)

similar_q_parameters = dict(
    community_id=TEST_COMMUNITY,
    query_string='hello world',
)

create_required_pms_tests('/api/view', view_parameters)
create_required_pms_tests('/api/recommend', recommend_parameters)
create_required_pms_tests('/api/similar_queries', similar_q_parameters)


def create_wrong_api_key_test(view_to_test, parameters):
    pms_to_use = {k: v for k, v in parameters.items()}
    pms_to_use['api_key'] = 'not the right key'

    def wrong_api_key_test(self):
        print(pms_to_use)
        response = self.client.get(view_to_test, data=pms_to_use)
        assert response.status_code == 403

    wrong_api_key_test.__name__ = 'test__{}__wrong_api_key__throws_403'\
        .format(view_to_test)
    setattr(TestParameters, wrong_api_key_test.__name__, wrong_api_key_test)

create_wrong_api_key_test('/api/view', view_parameters)
create_wrong_api_key_test('/api/recommend', recommend_parameters)
create_wrong_api_key_test('/api/similar_queries', similar_q_parameters)
