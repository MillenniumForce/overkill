"""This module acts as the main class to create and manage a worker server"""

import logging
import multiprocessing
import socketserver
import threading
import traceback
from typing import Dict, List, Tuple

from overkill.utils.server_data_classes import masterInfo
from overkill.utils.server_exceptions import AskTypeNotFoundError, ServerNotStartedError
from overkill.utils.server_messaging_standards import *
from overkill.utils.utils import *

_master = None  # master info
_id = None  # worker id


class _WorkerServer(socketserver.BaseRequestHandler):

    def __init__(self, request, client_address, server) -> None:
        socketserver.BaseRequestHandler.__init__(
            self, request, client_address, server)

    def handle(self):
        """Handle incoming connections

        :raises Exception: internal error in master server
        :raises askTypeNotFoundError: occurs when there is no case for an ask type
        """
        global _master, _id
        # TODO: what happens if there's more than 1024 bytes
        data = self.request.recv(1024)
        try:
            ask = decode_message(data)
            logging.info(ask)
            if ask["type"] == REJECT:
                raise Exception("Worker rejected")
            elif ask["type"] == ACCEPT:
                address = ask["master_address"]
                _master = masterInfo(address)
                logging.info(f"Master information: {_master}")
                _id = ask["id"]
            elif ask["type"] == DELEGATE_WORK:
                results = self.do_work(ask)
                send_message(encode_dict(
                    {"type": ACCEPT_WORK, "work_id": ask["work_id"], "data": results, "order": ask["order"]}), _master.address)
            else:
                raise AskTypeNotFoundError(f"No such type {ask['type']}")
        except AskTypeNotFoundError as e:
            logging.info(f"No such ask exists: {e}")
            return
        except Exception as e:
            logging.info(f"Could not handle request: {e}")
            logging.info(traceback.format_exc())
            return

    def do_work(self, ask: Dict) -> List:
        """After recieving work from the master server, execute the function on the data
        Current implementation uses 2 cores in parallel

        :param ask: dict of type, function, array
        :type ask: Dict
        :return: list of computed data
        :rtype: List
        """
        func = ask["function"]
        data = ask["array"]

        with multiprocessing.Pool(2) as p:
            results = p.map(func, data)

        return results


class _ThreadedWorkerServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


class Worker:

    def __init__(self, name: str) -> None:
        """Class acts as a high-level api to start and stop a worker server

        :param name: name of the worker server
        :type name: str
        """
        logging.basicConfig(filename="worker.log",
                            filemode="w",
                            format="%(levelname)s %(asctime)s - %(message)s",
                            level=logging.INFO)
        self.name = name
        self._server = None

        global _master, _id
        _master = None
        _id = None

    def start(self) -> None:
        """Start the server"""
        self.__init__(self.name)
        address = ('localhost', 0)
        self._server = _ThreadedWorkerServer(address, _WorkerServer)

        t = threading.Thread(target=self._server.serve_forever)
        t.setDaemon(True)
        t.start()

    def stop(self) -> None:
        """Stop the server"""
        if self._server is None:
            logging.warning("No server has been started")
        else:
            # TODO: notify master
            self._server.shutdown()

    def get_address(self) -> Tuple[str, int]:
        """Get the address of the worker server

        :return: tuple of ip, port
        :rtype: Tuple[str, int]
        """
        return self._server.server_address

    def connect_to_master(self, ip: str, port: int) -> None:
        """Given the address of the master try to connect to master

        :param ip: _description_
        :type ip: str
        :param port: _description_
        :type port: int
        :raises Exception: _description_
        """
        if self._server is None:
            raise ServerNotStartedError("No server has been started")
        connection_message = {"type": NEW_CONNECTION,
                              "name": self.name, "address": self.get_address()}
        try:
            send_message(encode_dict(connection_message), (ip, port))
        except ConnectionRefusedError:
            raise ConnectionRefusedError("Please check if the master address is correct")
