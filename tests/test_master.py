import random
import socket
from threading import Thread

from overkill.servers.master import Master
from overkill.utils.server_messaging_standards import (ACCEPT, DELEGATE_WORK,
                                                       DISTRIBUTE,
                                                       FINISHED_TASK)
from overkill.utils.utils import *
from tests.utils import MockWorker


def test_instantiation():
    """Test instantiation of Master"""
    m = Master()
    m.start()
    m.stop()


def test_new_worker():
    """Test adding a new worker to master"""
    m = Master()
    m.start()

    HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
    PORT = random.randint(1024, 65534)

    w = MockWorker(HOST, PORT)
    t = Thread(target=w.recieve_connection, daemon=True)
    t.start()
    w.connect_to_master(m.get_address())
    t.join()

    assert(w.recieved["type"] == ACCEPT)
   
    m.stop()


def test_recieve_work():
    """Test recieving and sending work from master"""
    m = Master()
    m.start()

    HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
    PORT = random.randint(1024, 65534)

    w = MockWorker(HOST, PORT)

    # 1: connecting to master
    t = Thread(target=w.recieve_connection, daemon=True)
    t.start()
    w.connect_to_master(m.get_address())
    t.join()
    assert(w.recieved["type"] == ACCEPT)

    # 2: recieve work from master
    t = Thread(target=w.recieve_connection, daemon=True)
    t.start()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(m.get_address())
        sock.sendall(encode_dict(
            {"type": DISTRIBUTE, "function": "foo", "array": [1, 2, 3]}))
        msg = decode_message(sock.recv(1024))
        assert(msg["type"] == FINISHED_TASK)
    t.join()
    assert(w.recieved["type"] == DELEGATE_WORK)

    m.stop()

