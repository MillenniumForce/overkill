"""General unsorted utility functions"""

import functools
import socket
import struct
import threading
from typing import Any, Dict, List, Tuple, Union
import dill

# sending and recieving data adapted from:
# https://stackoverflow.com/questions/17667903/python-socket-receive-large-amount-of-data
def _send_message(message: bytes, address: Tuple[str, int]) -> None:
    """Send a message to an arbitrary address. Function also
    prepends 4 bytes which includes the size of the message.
    Warning: does not handle any exceptions

    :param message: bytes to be sent
    :type message: bytes
    :param address: tuple of ip, port
    :type address: Tuple[str, int]
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(address)
        message = struct.pack(">I", len(message)) + message
        s.sendall(message)


def _socket_send_message(message: bytes, sock: socket.socket) -> None:
    """Send a message using a connected socket. Function also
    prepends 4 bytes which includes the size of the message.
    Warning: does not handle any exceptions

    :param message: bytes to be sent
    :type message: bytes
    :param sock: connected socket
    :type sock: socket.socket
    """
    message = struct.pack(">I", len(message)) + message
    sock.sendall(message)


def _recv_msg(sock: socket.socket) -> Union[None, bytearray]:
    """Recieve a message from the socket
    All messages should be prepended with the length,
    function will keep fetching data until message length

    :param sock: connected socket
    :type sock: socket.socket
    :return: recieved data, or none in case of no data
    :rtype: Union[None, bytearray]
    """
    raw_msglen = _recvall(sock, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
    return _recvall(sock, msglen)


def _recvall(sock: socket.socket, n: int) -> Union[None, bytearray]:
    """Recieve up to 'n' data

    :param sock: connected socket
    :type sock: socket.socket
    :param n: amount to recieve from the socket
    :type n: int
    :return: recieved data or none in the case of no data
    :rtype: Union[None, bytearray]
    """
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data


def _encode_dict(d: Dict) -> bytes:
    """Ecode the dictionary using dill.
    Dill is used to ensure that functions are encoded correctly
    Warning: does not handle any exceptions

    :param d: dictionary to encode
    :type d: Dict
    :return: dictionary in bytes form
    :rtype: bytes
    """
    return dill.dumps(d)


def _decode_message(b: bytes) -> Any:
    """Decode arbitrary bytes using Dill.
    Most common usecase is to decode a message.
    Dill is used to ensure functions are decoded correctly
    Warning: does not handle any exceptions

    :param b: bytes to decode
    :type b: bytes
    :return: decoded object (usually a dict)
    :rtype: Any
    """
    return dill.loads(b)


# https://stackoverflow.com/questions/952914/how-to-make-a-flat-list-out-of-a-list-of-lists
def _flatten(lst: List) -> List:
    """Flatten an arbitrary 2D list

    E.g. [[1], [2], [3]] = [1, 2, 3]

    :param lst: list to _flatten
    :type lst: List
    :return: flattened list
    :rtype: List
    """
    return [item for sublist in lst for item in sublist]


# https://stackoverflow.com/questions/489720/what-are-some-common-uses-for-python-decorators/490090#490090
def _synchronized(lock: threading.Lock) -> callable:
    """Synchronization wrapper

    :param lock: lock to acquire for synchronization
    :type lock: threading.Lock
    :return: wrapper
    :rtype: callable
    """
    def wrap(f):
        @functools.wraps(f)
        def newFunction(*args, **kw):
            with lock:
                return f(*args, **kw)
        return newFunction
    return wrap
