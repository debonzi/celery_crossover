# -*- encoding: utf-8 -*-
from crossover import Client
from examples.project_2.project import plus_callback, times_callback

p1_broker = "redis://localhost:6379/0"
project_1_client = Client(broker=p1_broker)

project_1_client.plus(x=340, y=210, callback=plus_callback)
project_1_client.times(x=340, y=210, callback=times_callback)
