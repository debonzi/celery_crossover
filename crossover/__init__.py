# -*- encoding: utf-8 -*-
import celery
from celery.utils.log import get_task_logger
from kombu import Exchange, Queue

from crossover.xrequests import requests
logger = get_task_logger(__name__)


CROSSOVER_QUEUE = '_crossover_router_queue.__dispatcher__'
CROSSOVER_ROUTER_NAME = "__crossover_router_dispatch__"


class CrossoverRouter(celery.Task):
    name = CROSSOVER_ROUTER_NAME

    def run(self, *args, **kwargs):
        task_name = kwargs.pop('task_name')
        logger.debug('Got Crossover task: {}'.format(task_name))
        _task = celery.current_app.tasks.get(task_name)
        if not _task:
            logger.error('Task {0} not found!'.format(task_name))
            return
        return _task.delay(*args, **kwargs)


def _register_celery_3(celery_app, queue):
    if celery_app.conf.CELERY_QUEUES:
        celery_app.conf.CELERY_QUEUES.append(queue)
    else:
        celery_app.conf.CELERY_QUEUES = [queue]


def _register_celery_4(celery_app, queue):
    if celery_app.conf.task_queues:
        celery_app.conf.task_queues.append(queue)
    else:
        celery_app.conf.task_queues = [queue]


def register_router(celery_app):
    celery_app.tasks.register(CrossoverRouter)
    queue = Queue(CROSSOVER_QUEUE, Exchange(CROSSOVER_QUEUE), routing_key=CROSSOVER_QUEUE)
    if not hasattr(celery_app.conf, 'task_queues'):  # Celery 3
        _register_celery_3(celery_app=celery_app, queue=queue)
    else:                                            # Celery 4
        _register_celery_4(celery_app=celery_app, queue=queue)


def _build_callback(task):
    if not hasattr(task.app.conf, 'broker_url'):  # Celery 3
        broker_url = task.app.conf.BROKER_URL
    else:                                         # Celery 4
        broker_url = task.app.conf.broker_url

    return {
        'broker': broker_url,
        'task': task.name
    }


def callback(auto_callback=False, bind_callback_meta=False):
    def _executor(func):
        def wrapped(*args, **kwargs):
            if 'callback' in kwargs:
                _callback = kwargs.pop('callback')
                if auto_callback:
                    CallBack(_callback)(result=func(*args, **kwargs))
                elif bind_callback_meta:
                    kwargs.update({"callback_meta": _callback})
                    func(*args, **kwargs)
                else:
                    func(*args, **kwargs)
                return
            if bind_callback_meta:  # and not 'callback' in kwargs
                kwargs.update({"callback_meta": None})
                func(*args, **kwargs)
            else:
                func(args, **kwargs)
        return wrapped
    return _executor


class CallBack(object):
    def __init__(self, callback_data):
        self.requester = None
        if callback_data:
            self.requester = _Requester(callback_data.get('broker'), callback_data.get('task'))

    def __call__(self, *args, **kwargs):
        if self.requester:
            self.requester(*args, **kwargs)


class _Requester(object):
    def __init__(self, broker, remote_task_name, task=CROSSOVER_ROUTER_NAME, queue=CROSSOVER_QUEUE):
        self.url = "{0}/{1}#{2}".format(broker, task, queue)
        self.remote_task_name = remote_task_name

    def __call__(self, *args, **kwargs):
        kwargs['task_name'] = self.remote_task_name
        if 'callback' in kwargs:
            kwargs['callback'] = _build_callback(kwargs['callback'])
        requests.post(self.url, json=kwargs)


class Client(object):
    def __init__(self, broker):
        self.broker = broker

    def call_task(self, remote_task_name, *args, **kwargs):
        req = _Requester(self.broker, remote_task_name)
        req(*args, **kwargs)

    def __getattr__(self, item):
        return _Requester(self.broker, item)
