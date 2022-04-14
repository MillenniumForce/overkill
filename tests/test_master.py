from overkill.servers.worker import Worker
from pandas import array
import pytest
import socket
from overkill.servers.master import Master
from overkill.utils.server_messaging_standards import DISTRIBUTE, NEW_CONNECTION, ACCEPT
import json
from overkill.utils.utils import *


def test_instantiation():
    m = Master()
    m.start()
    m.stop()


def test_new_worker():
    m = Master()
    m.start()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        connection_message = {"type": NEW_CONNECTION, "name": "test"}
        sock.connect(m.getAddress())
        sock.sendall(encode_dict(connection_message))

        received = decode_message(sock.recv(1024))

        print("Sent: {}".format(connection_message))
        print("Received: {}".format(received))
        assert(received["type"] == ACCEPT)

    m.stop()


def test_delegate_task():
    m = Master()
    m.start()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        # Create fake worker
        connection_message = {"type": NEW_CONNECTION, "name": "test"}
        sock.connect(m.getAddress())
        sock.sendall(encode_dict(connection_message))
        received = decode_message(sock.recv(1024))
        print("Sent: {}".format(connection_message))
        print("Received: {}".format(received))

        sock.sendall(encode_dict(
            {"type": DISTRIBUTE, "function": "foo", "array": [1, 2, 3]}))
        received = decode_message(sock.recv(1024))
        print("Sent: {}".format(connection_message))
        print("Received: {}".format(received))

    m.stop()
