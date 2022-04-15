import random
import pytest
from overkill.servers.worker import Worker
from overkill.servers.master import Master
import concurrent.futures
from tests.utils import mockWorker
import socket
from overkill.utils.utils import *
from overkill.utils.server_messaging_standards import *


def test_instantiation():
    w = Worker("test")
    w.start()
    w.stop()


def test_recieve_work():
    m = Master()
    m.start()

    HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
    PORT = random.randint(1024, 65534)

    w = mockWorker(HOST, PORT)
    w.connect_to_master(m.get_address())

    executor = concurrent.futures.ThreadPoolExecutor()
    future = executor.submit(w.recieve_connection)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(m.get_address())
        sock.sendall(encode_dict(
            {"type": DISTRIBUTE, "function": "foo", "array": [1, 2, 3]}))

    result = future.result(timeout=2)
    assert(result["type"] == DELEGATE_WORK)

    executor.shutdown()
    m.stop()