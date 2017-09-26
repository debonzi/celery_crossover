# -*- encoding: utf-8 -*-
from celery import Celery
from celery.utils.log import get_task_logger

import crossover

logger = get_task_logger(__name__)

app = Celery('tasks')
app.config_from_object('examples.project_1.celery_conf')

crossover.register_router(app)


@app.task(name='plus', queue='project_1')
@crossover.callback(auto_callback=True)
def plus(x, y):
    _add = x + y
    logger.info('Addition {0} + {1} = {2}'.format(x, y, _add))
    return _add


@app.task(name='times', queue='project_1')
@crossover.callback(bind_callback_meta=True)
def times(callback_meta, x, y):
    logger.info('Execution actual multiplication task.')
    calculate_times.delay(callback_meta, x, y)


@app.task(name='calculate_times', queue='project_1')
def calculate_times(callback_meta, x, y):
    _times = x * y
    logger.info('Multiplication {0} * {1} = {2}'.format(x, y, _times))
    crossover.CallBack(callback_meta)(result=_times)
