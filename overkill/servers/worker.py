"""This module acts as the main class to create and manage a worker server"""

import logging
import threading
from typing import Tuple

from overkill.servers._server_exceptions import (ServerAlreadyStartedError,
                                                 ServerNotStartedError)
from overkill.servers._server_messaging_standards import NEW_CONNECTION
from overkill.servers._utils import encode_dict, send_message

from ._worker import (ThreadedWorkerServer, WorkerServer,
                      close_connection_with_master, reset_globals)


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
        reset_globals()

    def start(self, ip: str = "localhost", port: int = 0) -> None:
        """Start the server on the given ip and port

        :param ip: server ip address to bind to, defaults to "localhost"
        :type ip: str, optional
        :param port: server port to bind to, defaults to 0
        :type port: int, optional
        """
        self.__init__(self.name)
        address = (ip, port)

        if self._server:
            raise ServerAlreadyStartedError()

        self._server = ThreadedWorkerServer(address, WorkerServer)
        t = threading.Thread(target=self._server.serve_forever, daemon=True)
        t.start()
        logging.info(f"Worker server running on {self.get_address()}")

    def stop(self) -> None:
        """Stop the server"""
        if self._server is None:
            logging.warning("No server has been started")
        else:
            close_connection_with_master()
            self._server.socket.close()
            self._server.shutdown()
            logging.info("Worker shutdown")

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
            raise ConnectionRefusedError(
                "Please check if the master address is correct")
