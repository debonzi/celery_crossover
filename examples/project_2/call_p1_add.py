# -*- encoding: utf-8 -*-
from crossover import Client, build_callback
from examples.project_2.project import plus_callback

p1_broker = "redis://localhost:6379/0"
project_1_client = Client(broker=p1_broker)

project_1_client.plus(x=340, y=210, callback=build_callback(plus_callback))
