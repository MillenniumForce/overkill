"""This module contains the main functionality of the master server"""

import logging
import threading
from typing import Tuple

from overkill.servers._server_exceptions import ServerAlreadyStartedError

from ._master import MasterServer, ThreadedMasterServer, reset_globals


__all__ = ["Master"]


class Master:
    """Use this class to start and stop a master server.

    The main methods of the class include ``start``, ``stop`` and ``get_address``.
    The usage of all the listed methods are fairly intuitive except for ``get_address`` which is
    mainly used to pass the address tuple to the user or for the worker.

    :Example:

    >>> from overkill.servers.master import Master
    >>> m = Master()
    >>> m.start()
    >>> m.get_address()
    ('127.0.0.1', 64406)
    >>> m.stop()

    **Note**: in the above example, the master won't always try to bind to the port 64406.
    The current implementation either lets the kernel decide the port (by default)
    or the user can also decide the port (not recommended).

    Instantiating the class will automatically start logging in 'master.log'.

    .. note::
        In the common scenario where you may want to connect to a worker that is on a different
        computer, you must use the local ip address of the computer which should look something
        like 192.168...

        The local ip should be passed as a parameter when using the ``start`` method of ``Master``.

        To find your computers local ip use the command
        ``ifconfig`` on mac/unix and ``ipconfig`` on windows.

    .. warning::
        It is not encouraged to have multiple instances of ``Master`` running in the same Python
        session, do so at your own risk.

    """

    def __init__(self) -> None:
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
