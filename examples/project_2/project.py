# -*- encoding: utf-8 -*-
import crossover

from celery import Celery
from celery.utils.log import get_task_logger

from examples.database import redis


logger = get_task_logger(__name__)

app = Celery('tasks')
app.config_from_object('examples.project_2.celery_conf')

crossover.register_router(app)

@app.task(queue='project_2')
def simple():
    return 'HELLO 2'

@app.task(name='plus_callback', queue='project_2')
def plus_callback(result):
    logger.info('Got Addition callback = {0}'.format(result))
    redis.db.set('plus_callback', result)


@app.task(name='times_callback', queue='project_2')
def times_callback(result):
    logger.info('Got Multiplication callback = {0}'.format(result))
    redis.db.set('times_callback', result)
