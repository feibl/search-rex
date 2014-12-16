from ..test_base import BaseTestCase
from datetime import datetime
from json import loads


TEST_COMMUNITY = 'test_community'


URL = '/api/'


def create_request(route, parameters):
    return '{}?{}'.format(
        route,
        '&'.join(['{}={}'.format(k, v) for k, v in parameters.items()])
    )


class TestParameters(BaseTestCase):

    def setUp(self):
        super(TestParameters, self).setUp()

    def test__view__wrong_time_format(self):
        parameters = dict(
            is_internal_record=True,
            record_id='Secret document',
            query_string='hello world',
            session_id=5556,
            timestamp=datetime(1999, 12, 24),
            api_key=self.app.config['API_KEY']
        )
        response = self.client.get(
            create_request(URL + 'view', parameters))

        assert response.status_code == 400
        assert loads(response.data)['message'] ==\
            'Parameter timestamp could not be parsed'


def create_throws_400_test(view_to_test, parameters, leave_out_pm):

    def do_test_expected(self):
        pms_to_use = {}
        for parameter in parameters.keys():
            if parameter == leave_out_pm:
                continue
            pms_to_use[parameter] = parameters[parameter]
        pms_to_use['api_key'] = self.app.config['API_KEY']

        response = self.client.get(
            create_request(URL + view_to_test, pms_to_use))
        assert response.status_code == 400
        assert loads(response.data)['message'] ==\
            'Missing required parameter {}'.format(leave_out_pm)
    return do_test_expected


def create_required_pms_tests(view, req_parameters):
    for leave_out_parameter in req_parameters.keys():

        test_method = create_throws_400_test(
            view, req_parameters,
            leave_out_parameter)
        test_method.__name__ = 'test___{}_omitting_{}__throws_404'\
            .format(view, leave_out_parameter)
        setattr(TestParameters, test_method.__name__, test_method)


action_parameters = dict(
    is_internal_record=True,
    record_id='Secret document',
    session_id=5556,
    timestamp=datetime(1999, 12, 24).isoformat(),
)

inspired_parameters = dict(
    include_internal_records=True,
    session_id=5556,
)

others_parameters = dict(
    include_internal_records=True,
    record_id='Secret document',
)

search_parameters = dict(
    include_internal_records=True,
    query_string='hello world',
)

recommend_parameters = dict(
    community_id=TEST_COMMUNITY,
    query_string='hello world',
)

similar_q_parameters = dict(
    query_string='hello world',
)

import_sim_parameters = dict(
    from_record_id='Secret document',
    to_record_id='other doc',
    from_record_is_internal=True,
    to_record_is_internal=True,
    similarity_value=0.78,
)

set_active_parameters = dict(
    record_id='Secret document',
    active=True,
)

create_required_pms_tests('view', action_parameters)
create_required_pms_tests('copy', action_parameters)
create_required_pms_tests('inspired_by_your_view_history', inspired_parameters)
create_required_pms_tests('inspired_by_your_copy_history', inspired_parameters)
create_required_pms_tests('other_users_also_viewed', others_parameters)
create_required_pms_tests('other_users_also_copied', others_parameters)
create_required_pms_tests('viewed_results_for_query', search_parameters)
create_required_pms_tests('copied_results_for_query', search_parameters)
create_required_pms_tests('recommend', recommend_parameters)
create_required_pms_tests('similar_queries', similar_q_parameters)
create_required_pms_tests('import_record_similarity', import_sim_parameters)
create_required_pms_tests('set_record_active', set_active_parameters)


def create_wrong_api_key_test(view_to_test, parameters):
    pms_to_use = {k: v for k, v in parameters.items()}
    pms_to_use['api_key'] = 'not the right key'

    def wrong_api_key_test(self):
        print(pms_to_use)
        response = self.client.get(
            create_request(URL + view_to_test, pms_to_use))
        assert response.status_code == 403

    wrong_api_key_test.__name__ = 'test__{}__wrong_api_key__throws_403'\
        .format(view_to_test)
    setattr(TestParameters, wrong_api_key_test.__name__, wrong_api_key_test)

create_wrong_api_key_test('view', action_parameters)
create_wrong_api_key_test('copy', action_parameters)
create_wrong_api_key_test('recommend', recommend_parameters)
create_wrong_api_key_test('similar_queries', similar_q_parameters)
create_wrong_api_key_test('inspired_by_your_view_history', inspired_parameters)
create_wrong_api_key_test('inspired_by_your_copy_history', inspired_parameters)
create_wrong_api_key_test('other_users_also_viewed', others_parameters)
create_wrong_api_key_test('other_users_also_copied', others_parameters)
create_wrong_api_key_test('viewed_results_for_query', search_parameters)
create_wrong_api_key_test('copied_results_for_query', search_parameters)
create_wrong_api_key_test('import_record_similarity', import_sim_parameters)
create_wrong_api_key_test('set_record_active', set_active_parameters)
