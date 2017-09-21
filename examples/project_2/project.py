# -*- encoding: utf-8 -*-
from celery import Celery
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

app = Celery('tasks', broker='redis://localhost:6379/1')


@app.task(name='crossover.plus_callback')
def plus_callback(result):
    logger.info('Got Addition callback = {0}'.format(result))
