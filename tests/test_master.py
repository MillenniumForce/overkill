from pandas import array
import pytest
import socket
from overkill.servers.master import Master
from overkill.utils.server_messaging_standards import DISTRIBUTE, ACCEPT
import json
from overkill.utils.utils import *
import concurrent.futures
from tests.utils import mockWorker
import random

def test_instantiation():
    m = Master()
    m.start()
    m.stop()


def test_new_worker():
    m = Master()
    m.start()

    HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
    PORT = random.randint(1024, 65534)

    w = mockWorker(HOST, PORT)

    executor = concurrent.futures.ThreadPoolExecutor()
    future = executor.submit(w.recieve_connection)

    w.connect_to_master(m.get_address())

    recieved = future.result(timeout=2)
    assert(recieved["type"] == ACCEPT)

    executor.shutdown()
    m.stop()

@pytest.mark.skip(reason="WIP")
def test_delegate_task():
    m = Master()
    m.start()

    HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
    PORT = random.randint(1024, 65534)

    executor = concurrent.futures.ThreadPoolExecutor()
    future = executor.submit(mock_worker, HOST, PORT)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(*m.get_address())
        sock.sendall(encode_dict(
            {"type": DISTRIBUTE, "function": "foo", "array": [1, 2, 3]}))
        received = decode_message(sock.recv(1024))
        print("Received: {}".format(received))

    m.stop()
