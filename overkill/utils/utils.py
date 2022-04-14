import functools
import socket
import json
from typing import Dict
from overkill.utils.server_messaging_standards import ENCODING
import dill


def send_message(message, address):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(address)
    s.sendall(message)
    s.close()


def encode_dict(d: Dict):
    return dill.dumps(d)


def decode_message(b: bytes):
    return dill.loads(b)


# https://stackoverflow.com/questions/952914/how-to-make-a-flat-list-out-of-a-list-of-lists
def flatten(t):
    return [item for sublist in t for item in sublist]


# https://stackoverflow.com/questions/489720/what-are-some-common-uses-for-python-decorators/490090#490090
def synchronized(lock):
    """ Synchronization decorator """
    def wrap(f):
        @functools.wraps(f)
        def newFunction(*args, **kw):
            with lock:
                return f(*args, **kw)
        return newFunction
    return wrap
