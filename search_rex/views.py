"""
In this module, the views of the recommender API are defined. According to
their definition, views are functions that take a web request and return a
web response. Therefore, they are the main entry points of the recommender
system. Moreover, they describe what the system is capable of and how the
system is accessed.
"""

from core import InvalidUsage
from flask import request
from flask import jsonify
from flask import Blueprint
from flask import current_app
from flask.ext.restful.inputs import datetime_from_iso8601
from functools import wraps

import logging

from services import report_view_action
from services import report_copy_action
import services

from .recommendations import get_recommender


logger = logging.getLogger(__name__)

rec_api = Blueprint('rec_api', __name__)


def api_key_required(view_function):
    """
    Decorator for view functions that checks if the correct API key is
    transferred
    """
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        if 'api_key' in request.args and\
                request.args.get('api_key') == current_app.config['API_KEY']:
            return view_function(*args, **kwargs)
        else:
            logger.info('Wrong API Key received')
            raise InvalidUsage(
                u'Invalid API key',
                status_code=403)

    return decorated_function


def parse_arg(
        request, arg_name, default_value=None, type=None, required=False):
    """
    Function for parsing arguments

    Arguments can be defined as required. In this case a InvalidUsage exception
    is thrown
    """
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
                u'Parameter {} could not be parsed'.format(arg_name),
                status_code=400)
        arg = default_value

    return arg


def parse_bool(string):
    """
    Parsing function for bool values
    """
    return string.lower() == 'true'


@rec_api.route('/api/view', methods=['GET'])
@api_key_required
def view():
    """
    Stores a view action that a user has performed on a record

    :param record_id: the id of the record
    :param is_internal_record: boolean indicating if record is internal
    :param session_id: the id of the session in which the action occurred
    :param timestamp: the timestamp of the action
    :param query_string: the query that has led to the action
    """
    is_internal_record = parse_arg(
        request, 'is_internal_record', required=True, type=parse_bool)
    record_id = parse_arg(request, 'record_id', required=True)
    session_id = parse_arg(request, 'session_id', required=True)
    timestamp = parse_arg(
        request, 'timestamp', required=True, type=datetime_from_iso8601)
    query_string = parse_arg(request, 'query_string', required=False)

    current_app.logger.info(
        'View action received. Record: %s, Session: %s, Query: %s',
        record_id, session_id, query_string)

    report_view_action(
        query_string=query_string, record_id=record_id, timestamp=timestamp,
        session_id=session_id, is_internal_record=is_internal_record)

    return jsonify(success=True)


@rec_api.route('/api/copy', methods=['GET'])
@api_key_required
def copy():
    """
    Stores a copy action that a user has performed on a record

    :param record_id: the id of the record
    :param is_internal_record: boolean indicating if record is internal
    :param session_id: the id of the session in which the action occurred
    :param timestamp: the timestamp of the action
    :param query_string: the query that has led to the action
    """

    is_internal_record = parse_arg(
        request, 'is_internal_record', required=True, type=parse_bool)
    record_id = parse_arg(request, 'record_id', required=True)
    session_id = parse_arg(request, 'session_id', required=True)
    timestamp = parse_arg(
        request, 'timestamp', required=True, type=datetime_from_iso8601)
    query_string = parse_arg(request, 'query_string', required=False)

    current_app.logger.info(
        'Copy action received. Record: %s, Session: %s, Query: %s',
        record_id, session_id, query_string)

    report_copy_action(
        query_string=query_string, record_id=record_id, timestamp=timestamp,
        session_id=session_id, is_internal_record=is_internal_record)

    return jsonify(success=True)


@rec_api.route('/api/influenced_by_your_history', methods=['GET'])
@api_key_required
def influenced_by_your_history():
    """
    Gets a list of recommended records based on a session's history

    :param session_id: the id of the session to which the records are
    recommended
    :param max_num_recs: the maximum number of recommendations to return
    :param include_internal_records: indicates if internal records should be
    recommended
    """
    include_internal_records = parse_arg(
        request, 'include_internal_records', required=True, type=parse_bool)
    print(include_internal_records)
    session_id = parse_arg(request, 'session_id', required=True)
    max_num_recs = parse_arg(
        request, 'max_num_recs', required=False, type=int)

    current_app.logger.info(
        'Influenced by your history request. Session: %s',
        session_id)

    recommender = get_recommender(include_internal_records)
    recs = recommender.influenced_by_your_history(
        session_id=session_id, max_num_recs=max_num_recs)

    return jsonify(results=[
        {'record_id': record_id, 'score': score} for record_id, score in recs
    ])


@rec_api.route('/api/other_users_also_used', methods=['GET'])
@api_key_required
def other_users_also_used():
    """
    Returns a list of records that were used together with the given one

    :param session_id: the id of the record
    :param max_num_recs: the maximum number of recommendations to return
    :param include_internal_records: indicates if internal records should be
    recommended
    """

    include_internal_records = parse_arg(
        request, 'include_internal_records', required=True, type=parse_bool)
    record_id = parse_arg(request, 'record_id', required=True)
    max_num_recs = parse_arg(
        request, 'max_num_recs', required=False, type=int)

    current_app.logger.info(
        'Other Users also used. Record: %s',
        record_id)

    recommender = get_recommender(include_internal_records)
    recs = recommender.other_users_also_used(
        record_id, max_num_recs=max_num_recs)

    return jsonify(results=[
        {'record_id': r_id, 'score': score} for r_id, score in recs
    ])


@rec_api.route('/api/recommended_search_results', methods=['GET'])
@api_key_required
def recommended_search_results():
    """
    Returns a list of records that were viewed after entering the query

    :param query_string: the query that was entered by the user
    :param max_num_recs: the maximum number of recommendations to return
    :param include_internal_records: indicates if internal records should be
    recommended
    """

    include_internal_records = parse_arg(
        request, 'include_internal_records', required=True, type=parse_bool)
    query_string = parse_arg(request, 'query_string', required=True)
    max_num_recs = parse_arg(
        request, 'max_num_recs', required=False, type=int)

    current_app.logger.info(
        'Recommended Search Results. Query: %s',
        query_string)

    recommender = get_recommender(include_internal_records)
    recs = recommender.recommend_search_results(
        query_string, max_num_recs=max_num_recs)

    return jsonify(results=[rec.serialize() for rec in recs])


@rec_api.route('/api/similar_queries', methods=['GET'])
@api_key_required
def similar_queries():
    """
    Returns a list of queries which are similar to the target query

    :param query_string: the query that was entered by the user
    """

    query_string = parse_arg(request, 'query_string', required=True)

    current_app.logger.info(
        'Similar Queries Request received: %s', query_string)

    similar_queries = get_recommender(True).get_similar_queries(
        query_string)

    return jsonify(
        {'results': [sim_q for sim_q in similar_queries]}
    )


@rec_api.route('/api/set_record_active', methods=['GET'])
@api_key_required
def set_record_active():
    """
    Sets a record active or inactive. Inactive records will not be recommended.

    :param record_id: the id of the record to be activated/deactivated
    :param active: boolean indicating if setting active or inactive
    """

    record_id = parse_arg(request, 'record_id', required=True)
    active = parse_arg(request, 'active', required=True, type=parse_bool)

    services.set_record_active(record_id, active)
    return jsonify(success=True)


@rec_api.route('/api/import_record_similarity', methods=['GET'])
@api_key_required
def import_record_similarity():
    """
    Imports a similarity value from one record to the other

    Only as many similarities as specified in max_sims_per_record are stored
    per record. If, by inclusion of the similarity, this value is exceeded,
    only the top similarities are preserved.

    :param from_record_id: the id of the record from which the similarity is
    directed
    :param from_is_internal: boolean indicating if from record is internal
    :param to_record_id: the id of the record to which the similarity is
    directed
    :param to_is_internal: boolean indicating if the to record is internal
    :param similarity: the similarity of the two records
    """
    from_record_id = parse_arg(request, 'from_record_id', required=True)
    to_record_id = parse_arg(request, 'to_record_id', required=True)
    from_is_internal = parse_arg(
        request, 'from_record_is_internal', required=True, type=parse_bool)
    to_is_internal = parse_arg(
        request, 'to_record_is_internal', required=True, type=parse_bool)
    sim_value = parse_arg(
        request, 'similarity_value', required=True, type=float)

    services.import_record_similarity(
        from_record_id, from_is_internal,
        to_record_id, to_is_internal,
        sim_value)

    return jsonify(success=True)


@rec_api.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response
