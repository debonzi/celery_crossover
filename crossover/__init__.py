# -*- encoding: utf-8 -*-
import posixpath
from crossover.xrequests import requests


def build_callback(task):
    queue = getattr(task, 'queue', None) or task.app.conf.task_default_queue
    return "{0}/{1}".format(task.app.conf.broker_url, posixpath.join(task.name, queue))


class CallBack(object):
    def __init__(self, url):
        self.url = url

    def __call__(self, url, **kwargs):
        requests.post(self.url, json=kwargs)


class _Requester(object):
    def __init__(self, broker, task, queue):
        self.url = "{0}/{1}".format(broker, posixpath.join(task, queue))

    def __call__(self, *args, **kwargs):
        requests.post(self.url, json=kwargs)


class Client(object):
    def __init__(self, broker, queue):
        self.broker = broker
        self.queue = queue

    def __getattr__(self, item):
        return _Requester(self.broker, "crossover.{0}".format(item), self.queue)
