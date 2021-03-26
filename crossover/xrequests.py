# -*- encoding: utf-8 -*-
import os
import requests as _requests
from rca.adapters import RedisCeleryAdapter

TIMEOUT = os.environ.get("CROSSOVER_CONN_TIMEOUT")
CROSSOVER_CONN_TIMEOUT = int(TIMEOUT) if TIMEOUT else None

requests = _requests.Session()
requests.mount(
    "redis://", RedisCeleryAdapter(first_connection_timeout=CROSSOVER_CONN_TIMEOUT)
)
