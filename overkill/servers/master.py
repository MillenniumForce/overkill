"""This module contains the main functionality of the master server"""

import logging
import socketserver
import threading
import traceback
from math import ceil
from random import random
from typing import Dict, Tuple

from overkill.utils.server_data_classes import _WorkOrder, _WorkerInfo
from overkill.utils.server_exceptions import AskTypeNotFoundError
from overkill.utils.server_messaging_standards import (_DISTRIBUTE, _NEW_CONNECTION, _NO_WORKERS_ERROR,
                                                       _REJECT, _ACCEPT, _ACCEPT_WORK,
                                                       _CLOSE_CONNECTION, _DELEGATE_WORK,
                                                       _FINISHED_TASK, _WORK_ERROR)
from overkill.utils.utils import (_decode_message, _encode_dict, _flatten, _recv_msg,
                                  _send_message, _socket_send_message, _synchronized)


_resources = 0  # server resources (must be >0)
_workers = {}  # dict of worker_id: _WorkerInfo
_work_orders = {}  # dict of work_id: workOrder


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
        data = _recv_msg(self.request)
        try:
            ask = _decode_message(data)
            logging.info(ask)
            if ask["type"] == _NEW_CONNECTION:
                self.welcome_new_worker(ask)
            elif ask["type"] == _DISTRIBUTE:
                if len(_workers) == 0:
                    err = {"type": _NO_WORKERS_ERROR}
                    _socket_send_message(_encode_dict(err), self.request)
                    return
                work_id = self.delegate_task(ask)
                _work_orders[work_id].event.wait()
                if _work_orders[work_id].error:
                    err = {"type": _WORK_ERROR,
                           "error": _work_orders[work_id].error}
                    _socket_send_message(_encode_dict(err), self.request)
                    return
                data = _flatten(_work_orders[work_id].data)
                work_order = _work_orders.pop(work_id)
                logging.info(f"Completed task {work_order}")
                _socket_send_message(
                    _encode_dict({"type": _FINISHED_TASK, "data": data}), self.request)
            elif ask["type"] == _ACCEPT_WORK:
                self.recieve_completed_task(ask)
            elif ask["type"] == _CLOSE_CONNECTION:
                resources = self.remove_worker(ask)
                logging.info(f"Worker shutdown, resources left: {resources}")
            elif ask["type"] == _WORK_ERROR:
                self.handle_work_error(ask)
            else:
                raise AskTypeNotFoundError(f"No such type {ask['type']}")
        except AskTypeNotFoundError as e:
            logging.info(f"No such ask exists: {e}")
            return
        except Exception as e:
            logging.info(f"Could not handle request: {e}")
            logging.info(traceback.format_exc())
            return

    @_synchronized(_lock)
    def welcome_new_worker(self, worker_details: Dict) -> None:
        """Process a new worker and either accept or reject
        Accept: add to list of workers
        Reject: send rejection message back to server

        :param worker_details: dictionary of type, name, address
        :type worker_details: Dict
        """
        global _resources, _workers
        try:
            new_worker = _WorkerInfo(
                hash(worker_details["name"] + str(random())),
                worker_details["name"],
                worker_details["address"]
            )
            _send_message(_encode_dict({"type": _ACCEPT, "id": new_worker.id,
                                        "master_address": self.server.server_address}), new_worker.address)
            _workers[new_worker.id] = new_worker
            _resources += 1
            logging.info("Resources at welcome new worker: %d", _resources)
        except Exception as e:
            _socket_send_message(_encode_dict({"type": _REJECT}), self.request)
            logging.info(f"Could not instantiate new worker: {e}")

    @_synchronized(_lock)
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

        for worker, (i, data) in zip(_workers.values(), enumerate(array_split)):
            # assume worker will always accept work
            work_request = {"type": _DELEGATE_WORK, "work_id": work_id,
                            "function": func, "array": data, "order": i}
            _send_message(_encode_dict(work_request), worker.address)

        _work_orders[work_id] = _WorkOrder(_resources, event)
        logging.info(_work_orders[work_id])

        return work_id

    @_synchronized(_lock)
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

    @_synchronized(_lock)
    def remove_worker(self, ask: Dict) -> int:
        """Remove worker by decrementing resource count and removing from the worker db

        :param ask: dictionary of type, worker_id
        :type ask: Dict
        :return: number of compute resources left
        :rtype: int
        """
        global _resources, _workers
        _resources -= 1
        _workers.pop(ask["id"])

        return _resources

    @_synchronized(_lock)
    def handle_work_error(self, ask: Dict) -> None:
        """Handle work error by setting the error message of the work order
        and by setting the work_id thread to true

        :param ask: _description_
        :type ask: Dict
        """
        global _work_orders
        _work_orders[ask["work_id"]].error = ask["error"]
        _work_orders[ask["work_id"]].event.set()


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
        _workers = {}
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
