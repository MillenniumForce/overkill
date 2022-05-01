"""This module contains the main master module abstractions"""

import logging
import socketserver
import threading
import traceback
from math import ceil
from random import random
from typing import Dict, Tuple

from overkill.servers._server_data_classes import (WorkerInfo, WorkError,
                                                   WorkOrder)
from overkill.servers._server_exceptions import AskTypeNotFoundError
from overkill.servers._server_messaging_standards import (ACCEPT, ACCEPT_WORK,
                                                          CLOSE_CONNECTION,
                                                          DELEGATE_WORK,
                                                          DISTRIBUTE,
                                                          FINISHED_TASK,
                                                          NEW_CONNECTION,
                                                          NO_WORKERS_ERROR,
                                                          REJECT, WORK_ERROR)
from overkill.servers._utils import (decode_message, encode_dict, flatten,
                                     recv_msg, send_message,
                                     socket_send_message, synchronized)


__all__ = [
    "ThreadedMasterServer",
    "MasterServer",
    "reset_globals"
]


_resources = 0  # server resources (must be >0)
_workers = {}  # dict of worker_id: WorkerInfo
_work_orders = {}  # dict of work_id: workOrder
_lock = threading.Lock()


def reset_globals():
    """Reset global variables:
    _resources, _workers, _work_orders
    """
    global _resources, _workers, _work_orders
    _resources = 0
    _workers = {}
    _work_orders = {}


class ThreadedMasterServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


class MasterServer(socketserver.BaseRequestHandler):

    def __init__(self, request, client_address, server) -> None:
        socketserver.BaseRequestHandler.__init__(
            self, request, client_address, server)

    def handle(self):
        """Handle incoming connections

        :raises Exception: internal error in master server
        :raises askTypeNotFoundError: occurs when there is no case for an ask type
        """
        data = recv_msg(self.request)
        try:
            ask = decode_message(data)
            logging.info(ask)

            if ask["type"] == NEW_CONNECTION:
                _welcome_new_worker(ask, self.server.server_address)

            elif ask["type"] == DISTRIBUTE:
                if len(_workers) == 0:
                    err = {"type": NO_WORKERS_ERROR}
                    socket_send_message(encode_dict(err), self.request)
                    return
                try:
                    work_id = _delegate_task(ask)
                except WorkError as e:
                    self.send_work_error(e)
                _work_orders[work_id].event.wait()
                if _work_orders[work_id].error:
                    self.send_work_error(_work_orders[work_id].error)
                    return
                data = flatten(_work_orders[work_id].data)
                work_order = _work_orders.pop(work_id)
                logging.info(f"Completed task {work_order}")
                socket_send_message(
                    encode_dict({"type": FINISHED_TASK, "data": data}), self.request)

            elif ask["type"] == ACCEPT_WORK:
                _recieve_completed_task(ask)

            elif ask["type"] == CLOSE_CONNECTION:
                resources = _remove_worker(ask)
                logging.info(f"Worker shutdown, resources left: {resources}")

            elif ask["type"] == WORK_ERROR:
                _handle_work_error(ask)

            else:
                raise AskTypeNotFoundError(f"No such type {ask['type']}")

        except AskTypeNotFoundError as e:
            logging.info(f"No such ask exists: {e}")
            return
        except Exception as e:
            logging.info(f"Could not handle request: {e}")
            logging.info(traceback.format_exc())
            return

    def send_work_error(self, error: WorkError):
        """Send an error message to the user

        :param error: error message
        :type error: WorkError
        """
        err = {"type": WORK_ERROR,
               "error": error}
        socket_send_message(encode_dict(err), self.request)


@synchronized(_lock)
def _welcome_new_worker(worker_details: Dict, master_address: Tuple[str, int]) -> None:
    """Process a new worker and either accept or reject
    Accept: add to list of workers
    Reject: send rejection message back to server

    :param worker_details: dictionary of type, name, address
    :type worker_details: Dict
    :param master_address: master's address to send to the worker
    :type master_adress: Tuple[str, int]
    """
    global _resources, _workers
    try:
        new_worker = WorkerInfo(
            hash(worker_details["name"] + str(random())),
            worker_details["name"],
            worker_details["address"]
        )
        send_message(encode_dict({"type": ACCEPT, "id": new_worker.id,
                                  "master_address": master_address}), new_worker.address)
        _workers[new_worker.id] = new_worker
        _resources += 1
        logging.info("Resources at welcome new worker: %d", _resources)
    except Exception as e:
        send_message(encode_dict({"type": REJECT}), new_worker.address)
        logging.info(f"Could not instantiate new worker: {e}")


@synchronized(_lock)
def _delegate_task(ask: Dict) -> int:
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

    try:
        logging.info("Array len: %d, num resources: %d",
                     len(array), _resources)
        size = ceil(len(array) / _resources)
        array_split = [array[i: i+size] for i in range(0, len(array), size)]
        work_id = hash(random())
        event = threading.Event()
    except Exception as e:
        raise WorkError(e)

    for worker, (i, data) in zip(_workers.values(), enumerate(array_split)):
        # assume worker will always accept work
        work_request = {"type": DELEGATE_WORK, "work_id": work_id,
                        "function": func, "array": data, "order": i}
        send_message(encode_dict(work_request), worker.address)

    _work_orders[work_id] = WorkOrder(_resources, event)
    logging.info(_work_orders[work_id])

    return work_id


@synchronized(_lock)
def _recieve_completed_task(ask: Dict) -> None:
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


@synchronized(_lock)
def _remove_worker(ask: Dict) -> int:
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


@synchronized(_lock)
def _handle_work_error(ask: Dict) -> None:
    """Handle work error by setting the error message of the work order
    and by setting the work_id thread to true

    :param ask: _description_
    :type ask: Dict
    """
    global _work_orders
    _work_orders[ask["work_id"]].error = ask["error"]
    _work_orders[ask["work_id"]].event.set()
