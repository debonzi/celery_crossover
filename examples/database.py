import time
from redis import Redis


class WorkerResultTimeout(Exception):
    """Result Timeout"""


class TestResultsDatabase(object):
    def __init__(self):
        self._db = Redis(db=8)

    def get(self, key, timeout=10):
        tick = 0.1
        steps = int(timeout / tick)
        for _ in range(steps):
            value = self._db.get(key)
            if value:
                return value
            time.sleep(0.1)
        raise WorkerResultTimeout

    def set(self, key, value):
        self._db.set(key, value)

    def clear_results(self):
        self._db.flushdb()


test_results = TestResultsDatabase()
p1_broker = Redis(db=0)
p2_broker = Redis(db=1)
