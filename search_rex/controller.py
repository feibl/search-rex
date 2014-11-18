from . import app
from . import rec_systems
from flask import request
from flask import jsonify
from flask.ext.restful import reqparse
from datetime import datetime
from werkzeug.urls import url_unquote


@app.route('/')
def index():
    return 'Welcome!'


view_arg_parser = reqparse.RequestParser()
view_arg_parser.add_argument('api_key', type=str, required=True)
view_arg_parser.add_argument(
    'community_id', type=str, default=app.config['DEFAULT_COMMUNITY'])
view_arg_parser.add_argument('query_string', type=str, required=True)
view_arg_parser.add_argument('record_id', type=str, required=True)
view_arg_parser.add_argument('session_id', type=str, required=True)
view_arg_parser.add_argument('timestamp', type=int, required=True)


@app.route('/api/view', methods=['GET'])
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

    if community_id not in rec_systems:
        return 'No Community called: {}'.format(community_id)
    rec = rec_systems[community_id]
    rec.register_hit(
        query_string=query_string, record_id=record_id,
        t_stamp=t_stamp, session_id=session_id)

    return 'Complete'


simq_arg_parser = reqparse.RequestParser()
simq_arg_parser.add_argument('api_key', type=str, required=True)
simq_arg_parser.add_argument(
    'community_id', type=str, default=app.config['DEFAULT_COMMUNITY'])
simq_arg_parser.add_argument('query_string', type=str, required=True)


@app.route('/api/similar_queries', methods=['GET'])
def similar_queries():
    '''Returns a list of queries which are similar to the target query'''
    args = simq_arg_parser.parse_args(request)

    api_key = args['api_key']
    community_id = args['community_id']
    query_string = url_unquote(args['query_string'])

    if community_id not in rec_systems:
        return 'No Community called: {}'.format(community_id)
    rec = rec_systems[community_id]
    similar_queries = rec.get_similar_queries(query_string)

    return jsonify(
        {'results': [sim_q for sim_q in similar_queries]}
    )


sreq_arg_parser = reqparse.RequestParser()
sreq_arg_parser.add_argument('api_key', type=str, required=True)
sreq_arg_parser.add_argument(
    'community_id', type=str, default=app.config['DEFAULT_COMMUNITY'])
sreq_arg_parser.add_argument('query_string', type=str, required=True)


@app.route('/api/recommend', methods=['GET'])
def recommend():
    '''Recommends search results other users from the same community where
    interested in when using a similar query'''
    args = sreq_arg_parser.parse_args(request)

    api_key = args['api_key']
    community_id = args['community_id']
    query_string = url_unquote(args['query_string'])

    if community_id not in rec_systems:
        return 'No Community called: {}'.format(community_id)
    rec = rec_systems[community_id]
    recommendations = rec.recommend(query_string)

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
