"""This module contains the main functionality of the master server"""

import logging
import threading
from typing import Tuple

from overkill.servers.utils.server_exceptions import ServerAlreadyStartedError

from ._master import MasterServer, ThreadedMasterServer, reset_globals


__all__ = ["Master"]


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
        reset_globals()

    def start(self, ip: str = "localhost", port: int = 0) -> None:
        """Start the server on the given ip and port

        :param ip: server ip address to bind to, defaults to "localhost"
        :type ip: str, optional
        :param port: server port to bind to, defaults to 0
        :type port: int, optional
        """
        self.__init__()
        address = (ip, port)

        if self._server:
            raise ServerAlreadyStartedError()

        self._server = ThreadedMasterServer(address, MasterServer)
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
