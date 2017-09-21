# Celery Crossover (Alpha)

## About
Celery crossover aim to make it easier to execute celery tasks from a diffent source code base in the most simple and yet reliable way.

![Use Case]
(/docs/CeleryCrossoverUseCase.png)

## Quick Example

Lets suppose Bob is a service that needs to execute a Task defined on Alice with the following code:

```python
# -*- encoding: utf-8 -*-
from celery import Celery

app = Celery('tasks')
app.config_from_object('celery_conf')

crossover.register_router(app)


@app.task(name='plus', queue='alice_queue')
def plus(x, y):
    _add = x + y
    return _add

```