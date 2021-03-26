import pytest
import subprocess
import signal

from redis import Redis

from examples.database import (
    p1_broker as p1_broker_,
    p2_broker as p2_broker_,
    test_results as test_results_,
)


class ProjectWorker(object):
    CMD_LINE = ""

    def start(self):
        self.sp = subprocess.Popen(self.CMD_LINE)

    def stop(self):
        self.sp.send_signal(signal.SIGINT)
        self.sp.wait()


class Project1Worker(ProjectWorker):
    CMD_LINE = "celery worker -A examples.project_1.project.app -l INFO".split(" ")


class Project2Worker(ProjectWorker):
    CMD_LINE = "celery worker -A examples.project_2.project.app -l INFO".split(" ")


def pytest_configure():
    Redis().flushall()


@pytest.fixture(scope="session", autouse=True)
def worker_1():
    pw = Project1Worker()
    pw.start()
    yield
    pw.stop()


@pytest.fixture(scope="session", autouse=True)
def worker_2():
    pw = Project2Worker()
    pw.start()
    yield
    pw.stop()


@pytest.fixture(scope="session")
def p1_broker():
    yield p1_broker_


@pytest.fixture(scope="session")
def p2_broker():
    yield p2_broker_


@pytest.fixture(scope="function")
def test_results():
    yield test_results_
    test_results_.clear_results()


@pytest.fixture(scope="session")
def p1_client():
    from crossover import Client

    p1_broker = "redis://localhost:6379/0"
    yield Client(broker=p1_broker)
