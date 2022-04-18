"""General unsorted utility functions"""

import functools
import socket
import threading
from typing import Any, Dict, List, Tuple
import dill


def _send_message(message: bytes, address: Tuple[str, int]) -> None:
    """Send a message to an arbitrary address.
    Warning: does not handle any exceptions

    :param message: bytes to be sent
    :type message: bytes
    :param address: tuple of ip, port
    :type address: Tuple[str, int]
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(address)
    s.sendall(message)
    s.close()


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
