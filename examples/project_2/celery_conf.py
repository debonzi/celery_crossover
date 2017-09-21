# -*- coding: utf-8 -*-
from kombu import Exchange, Queue

BROKER_URL = 'redis://localhost:6379/1'


CELERY_QUEUES = [
    Queue('project_2', Exchange('project_2'), routing_key='project_2')
]
