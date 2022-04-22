import socket
from overkill.servers.utils import utils
from overkill.servers.utils import server_messaging_standards
import types


def f(x):
    x += 10
    return x


def test(address):
    """DONT USE Helper function for testing"""
    f_no_globals = types.FunctionType(f.__code__, {})
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:

        connection_message = {"type": server_messaging_standards._DISTRIBUTE,
                              "function": f_no_globals, "array": [1, 2, 3, 4, 5]}
        sock.connect(address)
        enc = utils._encode_dict(connection_message)
        sock.sendall(len(enc))
        msg = utils._decode_message(sock.recv(10000))
        print(msg)


def connect(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("localhost", port))
    s.listen()
    conn, addr = s.accept()
    from overkill.servers.utils.utils import _recv_msg
    msg = _recv_msg(conn)
    s.close()
    return msg
