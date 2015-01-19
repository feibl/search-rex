from core import InvalidUsage
from flask import request
from flask import jsonify
from flask import Blueprint
from flask import current_app
from flask.ext.restful.inputs import datetime_from_iso8601
from functools import wraps

from services import report_view_action
from services import report_copy_action

from .recommendations import get_recommender


rec_api = Blueprint('rec_api', __name__)


def api_key_required(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        if 'api_key' in request.args and\
                request.args.get('api_key') == current_app.config['API_KEY']:
            return view_function(*args, **kwargs)
        else:
            raise InvalidUsage(
                u'Invalid API key',
                status_code=403)

    return decorated_function


def parse_arg(
        request, arg_name, default_value=None, type=None, required=False):
    try:
        arg = request.args[arg_name]
        if type is not None:
            arg = type(arg)
    except KeyError:
        if required:
            raise InvalidUsage(
                u'Missing required parameter {}'.format(arg_name),
                status_code=400)
        arg = default_value
    except ValueError:
        if required:
            raise InvalidUsage(
                u'Parameter {} could not be parsed'.format(
                    arg_name),
                status_code=400)
        arg = default_value

    return arg


@rec_api.route('/api/view', methods=['GET'])
@api_key_required
def view():
    """
    Reports that a view action occurred during a session
    """

    is_internal_record = parse_arg(
        request, 'is_internal_record', required=True, type=bool)
    record_id = parse_arg(request, 'record_id', required=True)
    session_id = parse_arg(request, 'session_id', required=True)
    timestamp = parse_arg(
        request, 'timestamp', required=True, type=datetime_from_iso8601)
    query_string = parse_arg(request, 'query_string', required=False)

    report_view_action(
        query_string=query_string, record_id=record_id, timestamp=timestamp,
        session_id=session_id, is_internal_record=is_internal_record)

    return jsonify(success=True)


@rec_api.route('/api/copy', methods=['GET'])
@api_key_required
def copy():
    """
    Reports that a copy action occurred during a session
    """

    is_internal_record = parse_arg(
        request, 'is_internal_record', required=True, type=bool)
    record_id = parse_arg(request, 'record_id', required=True)
    session_id = parse_arg(request, 'session_id', required=True)
    timestamp = parse_arg(
        request, 'timestamp', required=True, type=datetime_from_iso8601)
    query_string = parse_arg(request, 'query_string', required=False)

    report_copy_action(
        query_string=query_string, record_id=record_id, timestamp=timestamp,
        session_id=session_id, is_internal_record=is_internal_record)

    return jsonify(success=True)


@rec_api.route('/api/inspired_by_your_history', methods=['GET'])
@api_key_required
def inspired_by_your_history():
    """
    Gets a list of recommended records based on a session's history
    """
    include_internal_records = parse_arg(
        request, 'include_internal_records', required=True, type=bool)
    session_id = parse_arg(request, 'session_id', required=True)
    max_num_recs = parse_arg(
        request, 'max_num_recs', required=False, type=int)

    recommender = get_recommender(include_internal_records)
    recs = recommender.recommend_from_history(
        session_id=session_id, max_num_recs=max_num_recs)

    return jsonify(results=[
        {'record_id': record_id, 'score': score} for record_id, score in recs
    ])


@rec_api.route('/api/other_users_also_used', methods=['GET'])
@api_key_required
def other_users_also_used():
    """
    Returns a list of records that were used together with the given one
    """

    include_internal_records = parse_arg(
        request, 'include_internal_records', required=True, type=bool)
    record_id = parse_arg(request, 'record_id', required=True)
    max_num_recs = parse_arg(
        request, 'max_num_recs', required=False, type=int)

    recommender = get_recommender(include_internal_records)
    recs = recommender.recommend_similar_records(
        record_id, max_num_recs=max_num_recs)

    return jsonify(results=[
        {'record_id': r_id, 'score': score} for r_id, score in recs
    ])


@rec_api.route('/api/recommended_search_results', methods=['GET'])
@api_key_required
def recommended_search_results():
    """
    Returns a list of records that were viewed after entering the query
    """

    include_internal_records = parse_arg(
        request, 'include_internal_records', required=True, type=bool)
    query_string = parse_arg(request, 'query_string', required=True)
    max_num_recs = parse_arg(
        request, 'max_num_recs', required=False, type=int)

    recommender = get_recommender(include_internal_records)
    recs = recommender.recommend_search_results(
        query_string, max_num_recs=max_num_recs)

    return jsonify(results=[rec.serialize() for rec in recs])


@rec_api.route('/api/similar_queries', methods=['GET'])
@api_key_required
def similar_queries():
    """
    Returns a list of queries which are similar to the target query
    """

    query_string = parse_arg(request, 'query_string', required=True)
    community_id = 3
    similar_queries = get_recommender(True).get_similar_queries(
        query_string, community_id)

    return jsonify(
        {'results': [sim_q for sim_q in similar_queries]}
    )


@rec_api.route('/api/set_record_active', methods=['GET'])
@api_key_required
def set_record_active():
    """
    Sets a record active or inactive. Inactive records will not be recommended.
    """

    record_id = parse_arg(request, 'record_id', required=True)
    active = parse_arg(request, 'active', required=True, type=bool)

    return jsonify(success=True)


@rec_api.route('/api/import_record_similarity', methods=['GET'])
@api_key_required
def import_record_similarity():
    """
    Imports a similarity value of two records
    """

    from_record_id = parse_arg(request, 'from_record_id', required=True)
    to_record_id = parse_arg(request, 'to_record_id', required=True)
    from_is_internal = parse_arg(
        request, 'from_record_is_internal', required=True, type=bool)
    to_is_internal = parse_arg(
        request, 'to_record_is_internal', required=True, type=bool)
    sim_value = parse_arg(
        request, 'similarity_value', required=True, type=float)

    return jsonify(success=True)


@rec_api.route('/api/recommend', methods=['GET'])
@api_key_required
def recommend():
    '''Recommends search results other users from the same community where
    interested in when using a similar query'''
    community_id = parse_arg(request, 'community_id', required=True)
    query_string = parse_arg(request, 'query_string', required=True)

    recs = rec_service.recommend(
        query_string, community_id=community_id)

    return jsonify(
        {
            'results':
            [
                rec.serialize() for rec in recs
            ]
        }
    )


@rec_api.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response
