from flask import request
from flask import jsonify
from flask import Blueprint
from flask.ext.restful import reqparse
from datetime import datetime
from werkzeug.urls import url_unquote

from ..services import rec_service


rec_api = Blueprint('rec_api', __name__)


view_arg_parser = reqparse.RequestParser()
view_arg_parser.add_argument('api_key', type=str, required=True)
view_arg_parser.add_argument('community_id', type=str, required=True)
view_arg_parser.add_argument('query_string', type=str, required=True)
view_arg_parser.add_argument('record_id', type=str, required=True)
view_arg_parser.add_argument('session_id', type=str, required=True)
view_arg_parser.add_argument('timestamp', type=int, required=True)


@rec_api.route('/api/view', methods=['GET'])
def view():
    args = view_arg_parser.parse_args(request)

    api_key = args['api_key']
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
simq_arg_parser.add_argument('api_key', type=str, required=True)
simq_arg_parser.add_argument('community_id', type=str, required=True)
simq_arg_parser.add_argument('query_string', type=str, required=True)


@rec_api.route('/api/similar_queries', methods=['GET'])
def similar_queries():
    '''Returns a list of queries which are similar to the target query'''
    args = simq_arg_parser.parse_args(request)

    api_key = args['api_key']
    community_id = args['community_id']
    query_string = url_unquote(args['query_string'])

    similar_queries = rec_service.get_similar_queries(
        query_string, community_id)

    return jsonify(
        {'results': [sim_q for sim_q in similar_queries]}
    )


sreq_arg_parser = reqparse.RequestParser()
sreq_arg_parser.add_argument('api_key', type=str, required=True)
sreq_arg_parser.add_argument('community_id', type=str, required=True)
sreq_arg_parser.add_argument('query_string', type=str, required=True)


@rec_api.route('/api/recommend', methods=['GET'])
def recommend():
    '''Recommends search results other users from the same community where
    interested in when using a similar query'''
    args = sreq_arg_parser.parse_args(request)

    api_key = args['api_key']
    community_id = args['community_id']
    query_string = url_unquote(args['query_string'])

    recommendations = rec_service.recommend(
        query_string, community_id=community_id)

    return jsonify(
        {
            'results':
            [
                {
                    'record_id': r.record_id,
                    'relevance_score': r.relevance_score,
                    'target_query_relevance': r.target_query_relevance,
                    'popularity_rank': r.popularity_rank,
                    'related_queries': r.related_queries,
                    'last_interaction_time': r.last_interaction_time,
                } for r in recommendations]
        }
    )
