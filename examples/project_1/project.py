# -*- encoding: utf-8 -*-
from celery import Celery
from celery.utils.log import get_task_logger

from crossover import CallBack

logger = get_task_logger(__name__)

app = Celery('tasks', broker='redis://localhost:6379/0')


@app.task(name='crossover.add')
def add(x, y, callback):
    _add = x + y
    CallBack(callback)(result=_add)
    logger.info('Addition {0} + {1} = {2}'.format(x, y, _add))

