# -*- coding: utf-8 -*-
from kombu import Exchange, Queue

BROKER_URL = 'redis://localhost:6379/0'


CELERY_QUEUES = [
    Queue('project_1', Exchange('project_1'), routing_key='project_1')
]

