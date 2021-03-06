search-rex
==========

# Description
This application is an implementation of a recommender system that can be used parallel to a search engine in order to recommend search results and items to users. It has been designed for the HSR-Geodatenkompass, a geometadata application that is used by students and employees of the HSR in order to retrieve geodata for their projects and tasks. The system learns users' interests by recording their individual search queries and search result selections in the HSR-Geodatenkompass. The recommendations are generated by two different recommendation algorithms. The first one is an implementation of an item-based collaborative filtering approach. This algorithm recommends geodata records that have been often selected together with the records of the users' search histories. The second one is a case-based recommendation algorithm. This algorithm is capable of recommending search results to a particular query that was entered by a user. This is done by observing what users have selected in the past when they entered the same or a similar query.

# Application Setup 
In order to setup the application the following tools are required:
* Python 2.7 environment
* A database such as PostgreSQL
* virtualenv
* virtualenvwrapper

After having installed the above listed tools, the following steps are to be performed in order to setup a running instance of the application:

#### 1. Clone the project:
```
$ git clone git@github.com:feibl/search-rex.git
$ cd search_rex
```
#### 2. Create and initialize virtualenv for the project:
```
$ mkvirtualenv search_rex
$ pip install -r requirements.txt
```
#### 3. Set the configuration values for within the recsys_config.py file:
```python
class Config(object):
    SQLALCHEMY_DATABASE_URI =\
        'postgresql://postgres:password@localhost/search_rex'
    API_KEY = 'a18cccd4ff6cd3a54a73529e2145fd36'
    CELERY_BROKER_URL =\
        'sqla+postgresql://postgres:password@localhost/search_rex'
```
#### 4. Upgrade the database:
```
$ python manage.py db upgrade
```
#### 5. In a console, run the recommender application application:
```
$ python run.py
```
#### 6. In another console, run the Celery application:
```
$ celery -A search_rex.tasks worker --loglevel=info --beat
```

In the list entry 3, it can be seen that the API requires the specification of three configuration values. These configuration values are the following:
* `SQLALCHEMY_DATABASE_URI`: This configuration value tells the SQLAlchemy framework at which location the database can be found. It is specified in the form of a URI.
* `API_KEY`: This key is used to authenticate the caller who is calling one of the API's functions. It must be provided with every call directed to the API. Only if the key is correct, the function that is called is executed.
* `CELERY_BROKER_URL`: This configuration is needed in order to include the Celery task queue. Implementing this, Celery requires a solution to send and receive messages. This is achieved by using a message broker, a separate service where the messages are stored and consumed by the Celery workers. Examples of possible brokers are RabbitMQ, Redis or SQLAlchemy.


# API Functions

## View
Reports to the recommender system that a specific record was viewed during a particular session.

*Sample Call:*
```
<server_url>/api/1.0/view?`api_key`=51c54af0844d11e4b4a90800200c9a66&`record_id`=sogis45656&is_internal_record=true&`session_id`=0dd3d720844e11e4b4a90800200c9a66&query_string=moor%20Schwyz
```

* `api_key` (required): The key of the API in order to access its services. (e.g., "51c54af0844d11e4b4a90800200c9a66 ")
* `record_id` (required): The identifier of the record to which the action is directed. (e.g., "sogis45656 ")
* `session_id` (required): The identifier of the session that caused the action. (e.g., "0dd3d720844e11e4b4a90800200c9a66 ")
* `is_internal_record` (required): Indication of whether the record is internal or not. The values for this parameter can either be "true ", if the record is internal or "false", otherwise.
* `timestamp` (required): The date and time at which the action was recorded. It is described by using the ISO-8601 format "YYYY-MM-DDTHH:MM:SS ". (e.g., "2014-12-24T12:01:45")
* `query_string` (optional): By defining this parameter, the recommender is told that the action followed a previous query. The query is identified by the query string. (e.g., "moor Schwyz")

*Response:*
```
{
    "success": true
}
```

## Copy
Reports to the recommender system that a specific record was copied during a particular session.

*Sample Call:*
```
<server_url>/api/1.0/copy?`api_key`=51c54af0844d11e4b4a90800200c9a66&`record_id`=sogis45656&is_internal_record=true&`session_id`=0dd3d720844e11e4b4a90800200c9a66&query_string=moor%20Schwyz
```

* `api_key` (required): The key of the API in order to access its services. (e.g., "51c54af0844d11e4b4a90800200c9a66 ")
* `record_id` (required): The identifier of the record to which the action is directed. (e.g., "sogis45656 ")
* `session_id` (required): The identifier of the session that caused the action. (e.g., "0dd3d720844e11e4b4a90800200c9a66 ")
* `is_internal_record` (required): Indication of whether the record is internal or not. The values for this parameter can either be "true ", if the record is internal or "false ", otherwise.
* `timestamp` (required): The date and time at which the action was recorded. It is described by using the ISO-8601 format "YYYY-MM-DDTHH:MM:SS ". (e.g., "2014-12-24T12:01:45 ")
* `query_string` (optional): By defining this parameter, the recommender is told that the action followed a previous query. The query is identified by the query string. (e.g., "moor Schwyz ")

*Response:*
```
{
    "success": true
}
```

## Influenced by Your History
Gets a list of recommended records based on a session's history of viewed and copied records. The returned records are sorted by their relevance.
*Sample Call:*
```
<server_url>/api/1.0/influenced_by_your_history?`api_key`=51c54af0844d11e4b4a90800200c9a66&include_internal_records=true&`session_id`=0dd3d720844e11e4b4a90800200c9a66&max_num_recs=10
```

* `api_key` (required): The key of the API in order to access its services. (e.g., "51c54af0844d11e4b4a90800200c9a66 ")
* `session_id` (required): The identifier of the session for which the recommendations should be generated. (e.g., "0dd3d720844e11e4b4a90800200c9a66 ")
* `include_internal_records` (required): Indication of whether internal records should be included. The values for this parameter can either be "true ", if recommendations of internal records are allowed or "false ", otherwise.
* `max_num_recs` (optional): By defining this value, the caller can steer the maximal number of recommendations that are returned by the system (e.g., "20 ").

*Response:*
```
{
    "results": [
        {
            "`record_id`": "sogis389",
            "score": 0.9,
        },
        {
            "`record_id`": sogis45656,
            "score": 0.7,
        },
    ]
}
```

## Other Users Also Used
Given a record, the system returns a list of records that were viewed and copied by users who also have interacted with the record. The returned records are sorted by their relevance.

*Sample Call:*
```
<server_url>/api/1.0/other_users_also_used?`api_key`=51c54af0844d11e4b4a90800200c9a66&include_internal_records=true&`record_id`=sogis45656&max_num_recs=10
```
* `api_key` (required): The key of the API in order to access its services. (e.g., "51c54af0844d11e4b4a90800200c9a66 ")
* `include_internal_records` (required): Indication of whether internal records should be included. The values for this parameter can either be "true ", if recommendations of internal records are allowed or "false ", otherwise.
* `record_id` (required): The identifier of the record for which similar records should be retrieved. (e.g., "sogis45656 ")
* `max_num_recs` (optional): By defining this value, the caller can steer the maximal number of recommendations that are returned by the system (e.g., "20 ").

*Response:*
```
{
    "results": [
        {
            "`record_id`": "sogis389",
            "score": 0.9,
        },
        {
            "`record_id`": sogis45656,
            "score": 0.7,
        },
    ]
}
```

## Recommend Search Results
Given a query, the system returns a list of records that were found relevant by users after they have queried with the same or a similar query. The returned records are sorted by their relevance.
*Sample Call:*
```
<server_url>/api/1.0/recommend_search_results?`api_key`=51c54af0844d11e4b4a90800200c9a66&include_internal_records=true&query_string=moor%Schwyz&max_num_recs=10
```

* `api_key` (required): The key of the API in order to access its services. (e.g., "51c54af0844d11e4b4a90800200c9a66 ")
* `include_internal_records` (required): Indication of whether internal records should be included. The values for this parameter can either be "true ", if recommendations of internal records are allowed or "false ", otherwise.
* `query_string` (required): The query for which search results should be recommended. (e.g., "moor Schwyz ")
* `max_num_recs` (optional): By defining this value, the caller can steer the maximal number of recommendations that are returned by the system (e.g., "20 ").

*Response:*
```
{
    "results": [
        {
            "`record_id`": "sogis389",
            "score": 0.9,
            "total_hits": 29
            "last_interaction": "2014-12-24T12:01:45"
        },
        {
            "`record_id`": "sogis45656",
            "score": 0.7,
            "total_hits": 16
            "last_interaction": "2014-12-13T12:04:30"
        },
    ]
}
```

## Similar Queries
Given a query, the system returns a list of similar queries that other users have entered. The returned queries are sorted by their relevance.
*Sample Call:*
```
<server_url>/api/1.0/similar_queries?`api_key`=51c54af0844d11e4b4a90800200c9a66&query_string=moor%Schwyz&max_num_recs=10
```
* `api_key` (required): The key of the API in order to access its services. (e.g., "51c54af0844d11e4b4a90800200c9a66 ")
* `query_string` (required): The query for which related queries should be recommended. (e.g., "moor Schwyz ")
* `max_num_recs` (optional): By defining this value, the caller can steer the maximal number of recommendations that are returned by the system (e.g., "20 ").

*Response:*
```
{
    "results": [
        {
            "query": "moore in schwyz",
            "score": 0.9,
        },
        {
            "query": "hochmoor schwyz",
            "score": 0.7,
        },
    ]
}
```

## Import Record Similarity
By calling this function, it is possible to import a similarity value of two records. The similarity is directed from one record to the other. Its value describes the degree of resemblance of the two records. The higher this value, the more similar are the records.

*Sample Call:*
```
<server_url>/api/1.0/import_record_similarity?`api_key`=51c54af0844d11e4b4a90800200c9a66&from_`record_id`=sogis45656&to_`record_id`=sogis389&from_record_is_internal=true&to_record_is_internal=false&similarity_value=0.78
```

* `api_key` (required): The key of the API in order to access its services. (e.g., "51c54af0844d11e4b4a90800200c9a66 ")
* `from_record_id` (required): The identifier of the record from which the similarity is directed. (e.g., "sogis45656 ")
* `to_record_id` (required): The identifier of the record to the similarity is directed. (e.g., "sogis389 ")
* `from_record_is_internal` (required): Indication of whether the record from which the similarity is directed is internal or not. The values for this parameter can either be "true ", if the record is internal or "false ", otherwise.
* `to_record_is_internal` (required): Indication of whether the record to which the similarity is directed is internal or not. The values for this parameter can either be "true ", if the record is internal or "false ", otherwise.
* `similarity_value` (required): A float value ($$) describing the degree of similarity of the two records. The higher the value, the more similar are the records. (e.g., "0.78")

*Response:*
```
{
    "success": true
}
```

## Set Record Active
Sets a record active or inactive. Inactive records will not be recommended. 
*Sample Call:*
```
<server_url>/api/1.0/set_record_active?`api_key`=51c54af0844d11e4b4a90800200c9a66&`record_id`=sogis45656&active=false
```

* `api_key` (required): The key of thse API in order to access its services. (e.g., "51c54af0844d11e4b4a90800200c9a66 ")
* `record_id` (required): The identifier of the record that is to be set active or inactive. (e.g., "sogis45656 ")
* `active` (required): Indication of whether the record is to be set active or inactive. The values for this parameter can either be "true", if the record should be activated or "false", otherwise.
* \bottomrule

*Response:*
```
{
    "success": true
}
```
