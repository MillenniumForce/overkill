import socket
from overkill.utils import utils
from overkill.utils import server_messaging_standards


def f(x):
    return x


def test(address):
    """DONT USE Helper function for testing"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:

        connection_message = {"type": server_messaging_standards.DISTRIBUTE,
                              "function": f, "array": [1, 2, 3, 4, 5]}
        sock.connect(address)
        sock.sendall(utils.encode_dict(connection_message))
        msg = utils.decode_message(sock.recv(10000))
        print(msg)
