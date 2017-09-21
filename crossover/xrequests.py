# -*- encoding: utf-8 -*-
import requests as _requests
from rca.adapters import RedisCeleryAdapter

requests = _requests.Session()
requests.mount('redis://', RedisCeleryAdapter())
