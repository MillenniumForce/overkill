import random
import socket
from threading import Thread

from overkill.servers._server_messaging_standards import (ACCEPT,
                                                          DELEGATE_WORK,
                                                          DISTRIBUTE,
                                                          FINISHED_TASK)
from overkill.servers._utils import (decode_message, encode_dict, recv_msg,
                                     socket_send_message)
from overkill.servers.master import Master
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
    """Test sending work to master and recieving completed work
    input array should be fairly large to test
    """
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
    assert w.recieved["type"] == ACCEPT

    # 2: recieve work from master
    t = Thread(target=w.recieve_connection, daemon=True)
    t.start()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(m.get_address())
        socket_send_message(encode_dict(
            {"type": DISTRIBUTE, "function": f, "array": list(range(0, 10000))}), sock)
        msg = decode_message(recv_msg(sock))
        assert msg["type"] == FINISHED_TASK
    t.join()
    assert w.recieved["type"] == DELEGATE_WORK

    m.stop()


def f(x: int):
    return x*2
