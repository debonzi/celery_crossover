import pytest
import subprocess
import signal

from examples.database import redis as redis_

class ProjectWorker(object):
    CMD_LINE = ''

    def start(self):
        self.sp = subprocess.Popen(self.CMD_LINE)

    def stop(self):
        self.sp.terminate()


class Project1Worker(ProjectWorker):
    CMD_LINE = 'celery worker -A examples.project_1.project.app -l INFO'.split(' ')


class Project2Worker(ProjectWorker):
    CMD_LINE = 'celery worker -A examples.project_2.project.app -l INFO'.split(' ')


@pytest.fixture(scope='session')
def worker_1():
    pw = Project1Worker()
    pw.start()
    yield
    pw.stop()


@pytest.fixture(scope='session')
def worker_2():
    pw = Project2Worker()
    pw.start()
    yield
    pw.stop()


@pytest.fixture(scope='function')
def redis():
    yield redis_
    redis_.db.flushdb()


@pytest.fixture(scope='session')
def p1_client():
    from crossover import Client

    p1_broker = "redis://localhost:6379/0"
    yield Client(broker=p1_broker)
