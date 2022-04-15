import concurrent.futures
import random
import socket
from threading import Thread
import time

from overkill.servers.master import Master
from overkill.servers.worker import Worker
from overkill.utils.server_messaging_standards import *
from overkill.utils.utils import *
from tests.utils import MockWorker


def test_instantiation():
    """Test the instantiation of a new worker"""
    w = Worker("test")
    w.start()
    w.stop()
