from ..core import InvalidUsage
from flask import request
from flask import jsonify
from flask import Blueprint
from flask import current_app
from flask.ext.restful.inputs import datetime_from_iso8601
from functools import wraps

from ..services import rec_service


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
    is_internal_record = parse_arg(
        request, 'is_internal_record', required=True, type=bool)
    record_id = parse_arg(request, 'record_id', required=True)
    session_id = parse_arg(request, 'session_id', required=True)
    timestamp = parse_arg(
        request, 'timestamp', required=True, type=datetime_from_iso8601)
    query_string = parse_arg(request, 'query_string', required=False)
    community_id = 3
    rec_service.register_hit(
        query_string=query_string, community_id=community_id,
        record_id=record_id, t_stamp=timestamp, session_id=session_id)

    return jsonify(success=True)


@rec_api.route('/api/copy', methods=['GET'])
@api_key_required
def copy():
    is_internal_record = parse_arg(
        request, 'is_internal_record', required=True, type=bool)
    record_id = parse_arg(request, 'record_id', required=True)
    session_id = parse_arg(request, 'session_id', required=True)
    timestamp = parse_arg(
        request, 'timestamp', required=True, type=datetime_from_iso8601)
    query_string = parse_arg(request, 'query_string', required=False)
    community_id = 3
    rec_service.register_hit(
        query_string=query_string, community_id=community_id,
        record_id=record_id, t_stamp=timestamp, session_id=session_id)

    return jsonify(success=True)


@rec_api.route('/api/inspired_by_your_view_history', methods=['GET'])
@api_key_required
def inspired_by_your_view_history():
    include_internal_records = parse_arg(
        request, 'include_internal_records', required=True, type=bool)
    session_id = parse_arg(request, 'session_id', required=True)
    max_num_recs = parse_arg(
        request, 'max_num_recs', required=False, type=int)
    return jsonify(results=[])


@rec_api.route('/api/inspired_by_your_copy_history', methods=['GET'])
@api_key_required
def inspired_by_your_copy_history():
    include_internal_records = parse_arg(
        request, 'include_internal_records', required=True, type=bool)
    session_id = parse_arg(request, 'session_id', required=True)
    max_num_recs = parse_arg(
        request, 'max_num_recs', required=False, type=int)
    return jsonify(results=[])


@rec_api.route('/api/similar_queries', methods=['GET'])
@api_key_required
def similar_queries():
    '''Returns a list of queries which are similar to the target query'''
    community_id = parse_arg(request, 'community_id', required=True)
    query_string = parse_arg(request, 'query_string', required=True)

    similar_queries = rec_service.get_similar_queries(
        query_string, community_id)

    return jsonify(
        {'results': [sim_q for sim_q in similar_queries]}
    )


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
