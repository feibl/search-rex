from .recommendations import refresh_recommenders
from .factory import create_celery_app
from celery.decorators import periodic_task
from celery.utils.log import get_task_logger
from datetime import timedelta


celery = create_celery_app()
logger = get_task_logger(__name__)


@periodic_task(run_every=timedelta(minutes=30))
def refresh():
    logger.info("Start refreshing")
    refresh_recommenders()
    logger.info("Refreshing finished")
