import socket
from overkill.servers import _utils
from overkill.servers import _server_messaging_standards
from overkill.servers._utils import recv_msg
import types


def f(x):
    x += 10
    return x


def test(address):
    """DONT USE Helper function for testing"""
    f_no_globals = types.FunctionType(f.__code__, {})
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:

        connection_message = {"type": _server_messaging_standards.DISTRIBUTE,
                              "function": f_no_globals, "array": [1, 2, 3, 4, 5]}
        sock.connect(address)
        enc = _utils.encode_dict(connection_message)
        sock.sendall(len(enc))
        msg = _utils.decode_message(sock.recv(10000))
        print(msg)


def connect(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("localhost", port))
    s.listen()
    conn, addr = s.accept()
    msg = recv_msg(conn)
    s.close()
    return msg
