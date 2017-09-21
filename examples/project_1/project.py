# -*- encoding: utf-8 -*-
from celery import Celery
from celery.utils.log import get_task_logger

import crossover

logger = get_task_logger(__name__)

app = Celery('tasks')
app.config_from_object('examples.project_1.celery_conf')

crossover.register_router(app)


@app.task(name='plus', queue='project_1')
@crossover.exposed
def plus(x, y):
    _add = x + y
    logger.info('Addition {0} + {1} = {2}'.format(x, y, _add))
    return _add
