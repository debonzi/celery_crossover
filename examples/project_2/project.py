# -*- encoding: utf-8 -*-
from celery import Celery
from celery.utils.log import get_task_logger

import crossover

logger = get_task_logger(__name__)

app = Celery('tasks')
app.config_from_object('examples.project_2.celery_conf')

crossover.register_router(app)


@app.task(name='plus_callback', queue='project_2')
def plus_callback(result):
    logger.info('Got Addition callback = {0}'.format(result))


@app.task(name='times_callback', queue='project_2')
def times_callback(result):
    logger.info('Got Multiplication callback = {0}'.format(result))
