# -*- encoding: utf-8 -*-
import crossover

from celery import Celery
from celery.utils.log import get_task_logger

from examples.database import test_results


logger = get_task_logger(__name__)

app = Celery("tasks")
app.config_from_object("examples.project_1.celery_conf")

crossover.register_router(app)


@app.task(bind=True, queue="project_1")
@crossover.callback(auto_callback=True)
# Add crossover.callback just to ensure it
# can still be called as a local task.
def simple(self):
    assert self == simple
    return "HELLO 1"


@app.task(name="plus", queue="project_1")
@crossover.callback(auto_callback=True)
def plus(x, y):
    _add = x + y
    logger.info("Addition {0} + {1} = {2}".format(x, y, _add))
    return _add


@app.task(bind=True, name="times", queue="project_1")
@crossover.callback(bind_callback_meta=True)
def times(self, callback_meta, x, y):
    logger.info("Execution actual multiplication task.")
    calculate_times.delay(callback_meta, x, y)


@app.task(name="calculate_times", queue="project_1")
def calculate_times(callback_meta, x, y):
    _times = x * y
    logger.info("Multiplication {0} * {1} = {2}".format(x, y, _times))
    crossover.CallBack(callback_meta)(result=_times)


@crossover.metrics_subscribe()
def metrics_subscriber(metrics):
    test_results.set("dispatch_queue_time", metrics.dispatch_queue_time)
    test_results.set("task_name", metrics.task_name)
