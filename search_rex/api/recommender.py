from flask import request
from flask import jsonify
from flask import Blueprint
from flask import current_app
from flask import abort
from flask.ext.restful import reqparse
from datetime import datetime
from werkzeug.urls import url_unquote
from functools import wraps

from ..services import rec_service


rec_api = Blueprint('rec_api', __name__)


def api_key_required(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        if request.args.get('api_key') and\
                request.args.get('api_key') == current_app.config['API_KEY']:
            return view_function(*args, **kwargs)
        else:
            abort(403)
    return decorated_function


view_arg_parser = reqparse.RequestParser()
view_arg_parser.add_argument('community_id', type=str, required=True)
view_arg_parser.add_argument('query_string', type=str, required=True)
view_arg_parser.add_argument('record_id', type=str, required=True)
view_arg_parser.add_argument('session_id', type=str, required=True)
view_arg_parser.add_argument('timestamp', type=int, required=True)


@rec_api.route('/api/view', methods=['GET'])
@api_key_required
def view():
    args = view_arg_parser.parse_args(request)

    community_id = args['community_id']
    query_string = url_unquote(args['query_string'])
    record_id = args['record_id']
    session_id = args['session_id']
    t_stamp = datetime.fromtimestamp(
        args['timestamp']
    ).strftime('%Y-%m-%d %H:%M:%S')

    rec_service.register_hit(
        query_string=query_string, community_id=community_id,
        record_id=record_id, t_stamp=t_stamp, session_id=session_id)

    return 'Complete'


simq_arg_parser = reqparse.RequestParser()
simq_arg_parser.add_argument('community_id', type=str, required=True)
simq_arg_parser.add_argument('query_string', type=str, required=True)


@rec_api.route('/api/similar_queries', methods=['GET'])
@api_key_required
def similar_queries():
    '''Returns a list of queries which are similar to the target query'''
    args = simq_arg_parser.parse_args(request)

    community_id = args['community_id']
    query_string = url_unquote(args['query_string'])

    similar_queries = rec_service.get_similar_queries(
        query_string, community_id)

    return jsonify(
        {'results': [sim_q for sim_q in similar_queries]}
    )


sreq_arg_parser = reqparse.RequestParser()
sreq_arg_parser.add_argument('community_id', type=str, required=True)
sreq_arg_parser.add_argument('query_string', type=str, required=True)


@rec_api.route('/api/recommend', methods=['GET'])
@api_key_required
def recommend():
    '''Recommends search results other users from the same community where
    interested in when using a similar query'''
    args = sreq_arg_parser.parse_args(request)

    community_id = args['community_id']
    query_string = url_unquote(args['query_string'])

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
