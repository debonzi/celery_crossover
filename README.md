[![Build Status](https://travis-ci.org/debonzi/celery_crossover.svg?branch=master)](https://travis-ci.org/debonzi/celery_crossover)
[![PyPI](https://img.shields.io/pypi/v/celery_crossover.svg)](https://github.com/debonzi/celery_crossover)
[![PyPI](https://img.shields.io/pypi/pyversions/celery_crossover.svg)](https://github.com/debonzi/celery_crossover)
[![Coverage Status](https://coveralls.io/repos/github/debonzi/celery_crossover/badge.svg)](https://coveralls.io/github/debonzi/celery_crossover)

# Celery Crossover (Alpha)

## About
Celery crossover aims to make it easier to execute celery tasks from a diffent source code base in the most simple and yet reliable way.

![Use Case](https://github.com/debonzi/celery_crossover/blob/master/docs/CeleryCrossoverUseCase.png)

## Quick Examples

### 1) Simple Alice task execution triggered by Bob
Lets suppose Bob is a service that needs Alice to execute the task ```plus``` defined on Alice with the following code:

#### Alice:
 * celery_config.py
```python
# -*- coding: utf-8 -*-
from kombu import Exchange, Queue

BROKER_URL = 'redis://localhost:6379/1'
CELERY_QUEUES = [
    Queue('alice_queue', Exchange('alice_queue'), routing_key='alice_queue')
]
```

 * alice.py 
```python
# -*- encoding: utf-8 -*-
import crossover
from celery import Celery

app = Celery('tasks')
app.config_from_object('celery_conf')

# The line bellow will make Alice's Tasks usable by other services.
crossover.register_router(app)


@app.task(name='plus', queue='alice_queue')
def plus(x, y):
    _add = x + y
    return _add

```

#### Bob:
All that Bob need to do is:
* exec_task_on_alice.py 
```python
# -*- encoding: utf-8 -*-
from crossover import Client

alice_broker = "redis://localhost:6379/0"
alice_client = Client(broker=alice_broker)

alice_client.plus(x=340, y=210)

```

### 2) Alice task execution triggered by Bob with callback (Auto Callback)
In the same scenario described above, lets suppose Bob need to be notified (have a task executed) after Alice is done with the ```plus``` task.
For this case, all we have to do is decorate the Alice's task ```plus``` with```@crossover.callback(auto_callback=True)``` to have its returned value sent back to Bob. Also, Bob have to define and send to Alice a task to be called by Alice's callback.
That way, Alice and Bob could would be:

#### Alice:
 * alice_celery_config.py
```python
# -*- coding: utf-8 -*-
from kombu import Exchange, Queue

BROKER_URL = 'redis://localhost:6379/1'
CELERY_QUEUES = [
    Queue('alice_queue', Exchange('alice_queue'), routing_key='alice_queue')
]
```

 * alice.py 
```python
# -*- encoding: utf-8 -*-
import crossover
from celery import Celery

app = Celery('tasks')
app.config_from_object('celery_conf')

# The line bellow will make Alice's Tasks usable by other services.
crossover.register_router(app)


@app.task(name='plus', queue='alice_queue')
@crossover.callback(auto_callback=True)
def plus(x, y):
    _add = x + y
    return _add

```

#### Bob:
 * bob_celery_conf.py
```python
# -*- coding: utf-8 -*-
from kombu import Exchange, Queue

BROKER_URL = 'redis://localhost:6379/0'

CELERY_QUEUES = [
    Queue('bob_queue', Exchange('bob_queue'), routing_key='bob_queue')
]

```
 * bob.py
```python
# -*- encoding: utf-8 -*-
import crossover
from celery import Celery
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

app = Celery('tasks')
app.config_from_object('bob_celery_conf')

crossover.register_router(app)

@app.task(name='plus_callback', queue='bob_queue')
def plus_callback(result):
    logger.info('Got Addition callback = {0}'.format(result))

```

 * exec_task_on_alice.py 
```python
# -*- encoding: utf-8 -*-
from crossover import Client
from bob import plus_callback

alice_broker = "redis://localhost:6379/0"
alice_client = Client(broker=alice_broker)

alice_client.plus(x=340, y=210, callback=plus_callback)

```

### 3) Alice task execution triggered by Bob with callback (No Auto Callback)
In this case, everything is the same as 2) from Bob's perspective but lets suppose Alice's task cant calculate or
determine a response right away so it needs to pass (or persist) the callback metadata for further execution.
It can be done by using de decorator ```@crossover.callback``` with ```bind_callback_meta=True``` which will give
to the task function the callback metadata as its first parameters. Following an example of its usage:

 * alice.py

```python
# -*- encoding: utf-8 -*-
...

@app.task(name='plus', queue='alice_queue')
@crossover.callback(bind_callback_meta=True)
def plus(callback_meta, x, y):
    logger.info('Execution actual addition task.')
    calculate_addition.delay(callback_meta, x, y):


@app.task(name='calculate_addition', queue='project_1')
def calculate_addition(callback_meta, x, y):
    _add = x + y
    logger.info('Addition {0} + {1} = {2}'.format(x, y, _add))
    crossover.CallBack(callback_meta)(result=_add)
```
