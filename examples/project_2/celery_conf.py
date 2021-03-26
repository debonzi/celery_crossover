# -*- coding: utf-8 -*-
from kombu import Exchange, Queue

BROKER_URL = "redis://localhost:6379/1"
CELERY_RESULT_BACKEND = "redis://localhost:6379/11"
CELERYD_PREFETCH_MULTIPLIER = 1
CELERYD_CONCURRENCY = 1


CELERY_QUEUES = [
    Queue("project_2", Exchange("project_2"), routing_key="project_2"),
    Queue("celery", Exchange("celery"), routing_key="celery"),
]
