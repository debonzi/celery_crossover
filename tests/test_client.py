# -*- coding: utf-8 -*-
import types
from crossover import Client
from crossover import _Requester


def test_client_attributes():
    client = Client("redis://localhost:6379/0")
    assert isinstance(client, Client)
    assert isinstance(client.test, _Requester)
    assert isinstance(client.call_task, types.MethodType)
