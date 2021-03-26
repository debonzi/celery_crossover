# -*- coding: utf-8 -*-
from kombu import Exchange, Queue

BROKER_URL = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND = "redis://localhost:6379/10"
CELERYD_PREFETCH_MULTIPLIER = 1
CELERYD_CONCURRENCY = 4

CELERY_QUEUES = [
    Queue("project_1", Exchange("project_1"), routing_key="project_1"),
    Queue("celery", Exchange("celery"), routing_key="celery"),
]

CELERY_ACKS_LATE = True
