# -*- encoding: utf-8 -*-
import time
import celery
from celery.utils.log import get_task_logger
from kombu import Exchange, Queue

from crossover.xrequests import requests

logger = get_task_logger(__name__)


CROSSOVER_QUEUE = "_crossover_router_queue.__dispatcher__"
CROSSOVER_ROUTER_NAME = "__crossover_router_dispatch__"


class metrics_subscribe(object):
    subscribers_ = set()

    def __call__(self, wrapped):
        self.subscribers_.update([wrapped])
        return wrapped

    @classmethod
    def call_subscribers(cls, metrics):
        for s in cls.subscribers_:
            s(metrics)


class TaskNotFoundError(Exception):
    """ Raised when requested task is not found."""


class CrossoverRouter(celery.Task):
    CELERY_4_VERSION = celery.version_info_t(4, 0, 0, "", "")
    name = CROSSOVER_ROUTER_NAME

    def run(self, *args, **kwargs):
        metrics = CrossoverMetrics.load(kwargs)
        if metrics:
            metrics.set_remote_time()
            metrics_subscribe.call_subscribers(metrics)

        app = celery.current_app if celery.VERSION < self.CELERY_4_VERSION else self.app
        task_name = kwargs.pop("task_name")

        logger.debug("Got Crossover task: {}".format(task_name))
        _task = app.tasks.get(task_name)
        if not _task:
            raise TaskNotFoundError('Task "{0}" not found!'.format(task_name))
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
    CrossoverRouter.bind(celery_app)
    celery_app.tasks.register(CrossoverRouter)

    queue = Queue(
        CROSSOVER_QUEUE, Exchange(CROSSOVER_QUEUE), routing_key=CROSSOVER_QUEUE
    )
    if not hasattr(celery_app.conf, "task_queues"):  # Celery 3
        _register_celery_3(celery_app=celery_app, queue=queue)
    else:  # Celery 4
        _register_celery_4(celery_app=celery_app, queue=queue)


def _build_callback(task, bind_metrics):
    if not hasattr(task.app.conf, "broker_url"):  # Celery 3
        broker_url = task.app.conf.BROKER_URL
    else:  # Celery 4
        broker_url = task.app.conf.broker_url

    return {
        "broker": broker_url,
        "task": task.name,
        "bind_metrics": bind_metrics,
    }


def callback(auto_callback=False, bind_callback_meta=False):
    def _executor(func):
        def wrapped(*args, **kwargs):
            if "callback" in kwargs:
                _callback = kwargs.pop("callback")
                if auto_callback:
                    return CallBack(_callback)(result=func(*args, **kwargs))
                elif bind_callback_meta:
                    kwargs.update({"callback_meta": _callback})
                    return func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
            if bind_callback_meta:  # and not 'callback' in kwargs
                kwargs.update({"callback_meta": None})
                return func(*args, **kwargs)
            else:
                return func(*args, **kwargs)

        return wrapped

    return _executor


class CallBack(object):
    def __init__(self, callback_data):
        self.requester = None
        if callback_data:
            self.requester = _Requester(
                callback_data.get("broker"),
                callback_data.get("task"),
            )
        self.bind_metrics = callback_data.get("bind_metrics", False)

    def __call__(self, *args, **kwargs):
        if self.requester:
            kwargs.update({"bind_metrics": self.bind_metrics})
            self.requester(*args, **kwargs)


class _Requester(object):
    def __init__(
        self,
        broker,
        remote_task_name,
        task=CROSSOVER_ROUTER_NAME,
        queue=CROSSOVER_QUEUE,
    ):
        self.url = "{0}/{1}#{2}".format(broker, task, queue)
        self.remote_task_name = remote_task_name

    def __call__(self, *args, **kwargs):
        bind_metrics = kwargs.pop("bind_metrics", False)

        kwargs["task_name"] = self.remote_task_name
        if "callback" in kwargs:
            kwargs["callback"] = _build_callback(
                task=kwargs["callback"],
                bind_metrics=bind_metrics,
            )

        if bind_metrics:
            metrics = CrossoverMetrics(task_name=self.remote_task_name)
            metrics.set_origin_time()
            kwargs["metrics"] = metrics.dump()

        requests.post(self.url, json=kwargs)


class CrossoverMetrics(object):
    def __init__(
        self,
        task_name=None,
        origin_time=None,
        remote_time=None,
    ):
        self.task_name = task_name
        self.origin_time = origin_time
        self.remote_time = remote_time

    @property
    def queue_time(self):
        if not all(self.origin_time, self.remote_time):
            return None
        return self.remote_time - self.origin_time

    def set_origin_time(self):
        self.origin_time = time.time()

    def set_remote_time(self):
        self.remote_time = time.time()

    @classmethod
    def load(cls, xover_payload):
        metrics = xover_payload.pop("metrics", None)
        if not metrics:
            return None
        return cls(
            task_name=metrics.get("_task_name"),
            origin_time=metrics.get("_origin_time"),
            remote_time=metrics.get("_remote_time"),
        )

    def dump(self):
        return dict(
            _task_name=self.task_name,
            _origin_time=self.origin_time,
            _remote_time=self.remote_time,
        )

    @property
    def dispatch_queue_time(self):
        if all([self.origin_time, self.remote_time]):
            return self.remote_time - self.origin_time


class Client(object):
    def __init__(self, broker):
        self.broker = broker

    def call_task(self, remote_task_name, *args, **kwargs):
        req = _Requester(self.broker, remote_task_name)
        req(*args, **kwargs)

    def __getattr__(self, item):
        return _Requester(self.broker, item)
