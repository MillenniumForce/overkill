import random
import socket
from threading import Thread

from overkill.servers.master import Master
from overkill.utils.server_messaging_standards import (_ACCEPT, _DELEGATE_WORK,
                                                       _DISTRIBUTE,
                                                       _FINISHED_TASK)
from overkill.utils.utils import _encode_dict, _decode_message
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

    assert(w.recieved["type"] == _ACCEPT)

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
    assert w.recieved["type"] == _ACCEPT

    # 2: recieve work from master
    t = Thread(target=w.recieve_connection, daemon=True)
    t.start()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(m.get_address())
        sock.sendall(_encode_dict(
            {"type": _DISTRIBUTE, "function": f, "array": [1, 2, 3]}))
        msg = _decode_message(sock.recv(1024))
        assert msg["type"] == _FINISHED_TASK
    t.join()
    assert w.recieved["type"] == _DELEGATE_WORK

    m.stop()


def f(x: int):
    return x*2
