"""
Due to the reason that the recommendation components hold the data that they
need in the local memory, it is required that they are told periodically to
reload the data from the database. This is the task of a worker thread that
executes such a call from time to time. The tasks module implements the
function that needs to be executed in order to refresh the recommender system.
This function is run as background task by a Celery instance.
"""

from .recommendations import refresh_recommenders
from .factory import create_celery_app
from celery.decorators import periodic_task
from celery.utils.log import get_task_logger
from datetime import timedelta


celery = create_celery_app()
logger = get_task_logger(__name__)


@periodic_task(run_every=timedelta(minutes=30))
def refresh():
    """
    Calls the recommender instances' refresh function every 30 minutes
    """
    logger.info("Start refreshing")
    refresh_recommenders()
    logger.info("Refreshing finished")
