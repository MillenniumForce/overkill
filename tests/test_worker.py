import pytest
from overkill.servers.worker import Worker
from overkill.servers.master import Master


def test_instantiation():
    w = Worker("test")
    w.start()
    w.stop()
