# -*- encoding: utf-8 -*-
from celery import Celery
from celery.utils.log import get_task_logger

import crossover

logger = get_task_logger(__name__)

app = Celery('tasks', broker='redis://localhost:6379/0')


@app.task(name='crossover.plus')
@crossover.reply_callback
def plus(x, y):
    _add = x + y
    logger.info('Addition {0} + {1} = {2}'.format(x, y, _add))
    return _add
