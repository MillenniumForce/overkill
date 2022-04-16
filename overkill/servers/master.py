"""This module contains the main functionality of the master server"""

import logging
import socketserver
import threading
import traceback
from math import ceil
from random import random
from typing import Dict, Tuple

from overkill.utils.server_data_classes import WorkOrder, workerInfo
from overkill.utils.server_exceptions import AskTypeNotFoundError
from overkill.utils.server_messaging_standards import *
from overkill.utils.utils import (decode_message, encode_dict, flatten,
                                  send_message, synchronized)

# locking https://stackoverflow.com/questions/489720/what-are-some-common-uses-for-python-decorators/490090#490090

_resources = 0 # server resources (must be >0)
_workers = [] # array of workerInfo
_work_orders = {} # dict of work_id: workOrder


class _MasterServer(socketserver.BaseRequestHandler):

    _lock = threading.Lock()

    def __init__(self, request, client_address, server) -> None:
        socketserver.BaseRequestHandler.__init__(
            self, request, client_address, server)

    def handle(self):
        """Handle incoming connections

        :raises Exception: internal error in master server
        :raises askTypeNotFoundError: occurs when there is no case for an ask type
        """
        # TODO: what happens if there's more than 1024 bytes
        data = self.request.recv(1024)
        try:
            ask = decode_message(data)
            logging.info(ask)
            if ask["type"] == NEW_CONNECTION:
                self.welcome_new_worker(ask)
            elif ask["type"] == DISTRIBUTE:
                work_id = self.delegate_task(ask)
                _work_orders[work_id].event.wait()
                data = flatten(_work_orders[work_id].data)
                work_order = _work_orders.pop(work_id)
                logging.info(f"Completed task {work_order}")
                self.request.sendall(encode_dict(
                    {"type": FINISHED_TASK, "data": data}))
            elif ask["type"] == ACCEPT_WORK:
                self.recieve_completed_task(ask)
            else:
                raise AskTypeNotFoundError(f"No such type {ask['type']}")
        except AskTypeNotFoundError as e:
            logging.info(f"No such ask exists: {e}")
            return
        except Exception as e:
            logging.info(f"Could not handle request: {e}")
            logging.info(traceback.format_exc())
            return

    @synchronized(_lock)
    def welcome_new_worker(self, worker_details: Dict) -> None:
        """Process a new worker and either accept or reject
        Accept: add to list of workers
        Reject: send rejection message back to server

        :param worker_details: dictionary of type, name, address
        :type worker_details: Dict
        """
        global _resources, _workers
        try:
            new_worker = workerInfo(
                hash(worker_details["name"] + str(random())),
                worker_details["name"],
                worker_details["address"]
            )
            send_message(encode_dict({"type": ACCEPT, "id": new_worker.id,
                                      "master_address": self.server.server_address}), new_worker.address)
            _workers.append(new_worker)
            _resources += 1
            logging.info("Resources at welcome new worker: %d", _resources)
        except Exception as e:
            self.request.sendall(encode_dict({"type": REJECT}))
            logging.info(f"Could not instantiate new worker: {e}")

    @synchronized(_lock)
    def delegate_task(self, ask: Dict) -> int:
        """Delegate tasks to each worker
        All tasks are currently split evenly between workers

        :param ask: dictionary of type, function, array
        :type ask: Dict
        :return: work id of the delegated task
        :rtype: int
        """
        global _work_orders
        func = ask["function"]
        array = ask["array"]

        logging.info("Array len: %d, num resources: %d",
                     len(array), _resources)
        size = ceil(len(array) / _resources)
        array_split = [array[i: i+size] for i in range(0, len(array), size)]
        work_id = hash(random())
        event = threading.Event()

        for worker, (i, data) in zip(_workers, enumerate(array_split)):
            # assume worker will always accept work
            work_request = {"type": DELEGATE_WORK, "work_id": work_id,
                            "function": func, "array": data, "order": i}
            send_message(encode_dict(work_request), worker.address)

        _work_orders[work_id] = WorkOrder(_resources, event)
        logging.info(_work_orders[work_id])

        return work_id

    @synchronized(_lock)
    def recieve_completed_task(self, ask: Dict) -> None:
        """Recieve a completed task from a worker

        :param ask: dictionary of type, work_id, data (array), order (to insert into the correct position)
        :type ask: Dict
        """
        global _work_orders
        work_id = ask["work_id"]
        new_data = ask["data"]
        order = ask["order"]
        _work_orders[work_id].update(new_data, order)
        logging.info(_work_orders[work_id])
        if _work_orders[work_id].progress == 1:
            _work_orders[work_id].event.set()


class _ThreadedMasterServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


class Master:

    def __init__(self) -> None:
        """Class acts as a high-level api to start and stop a master server"""
        logging.basicConfig(filename="master.log",
                            filemode="w",
                            format="%(levelname)s %(asctime)s - %(message)s",
                            level=logging.INFO)
        self._server = None
        self.ip = None
        self.port = None

        global _resources, _workers, _work_orders
        _resources = 0
        _workers = []
        _work_orders = {}

    def start(self, ip: str = "localhost", port: int = 0) -> None:
        """Start the server on the given ip and port

        :param ip: server ip address to bind to, defaults to "localhost"
        :type ip: str, optional
        :param port: server port to bind to, defaults to 0
        :type port: int, optional
        """
        self.__init__()
        address = (ip, port)
        self._server = _ThreadedMasterServer(address, _MasterServer)
        logging.info(f"Master server running on {self.get_address()}")

        t = threading.Thread(target=self._server.serve_forever, daemon=True)
        t.start()

    def stop(self) -> None:
        """Stop the server"""
        if self._server is None:
            logging.error("No server has been started")
            return
        self._server.socket.close()
        self._server.shutdown()

    def get_address(self) -> Tuple[str, int]:
        """Get the address of the master server

        :return: tuple of ip, port
        :rtype: Tuple[str, int]
        """
        return self._server.server_address  # find out what port we were given
