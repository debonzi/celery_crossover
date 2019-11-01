import time
from redis import Redis


class WorkerResultTimeout(Exception):
    """Result Timeout"""


class RedisTestDatabase(object):
    def __init__(self):
        self.db = Redis(db=8)

    def get(self, key, timeout=10):
        tick = 0.1
        steps = int(timeout/tick)
        for _ in range(steps):
            value = self.db.get(key)
            if value:
                return value
            time.sleep(0.1)
        raise WorkerResultTimeout


redis = RedisTestDatabase()
