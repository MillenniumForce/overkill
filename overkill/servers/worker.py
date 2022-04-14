import logging
import threading
import socketserver
import multiprocessing
import socket
from typing import Dict, List
import dill
import traceback

from overkill.utils.server_exceptions import askTypeNotFoundError
from overkill.utils.server_data_classes import masterInfo
from overkill.utils.server_messaging_standards import *
from overkill.utils.utils import *


_master = None  # master info
_id = None  # worker id


class _WorkerServer(socketserver.BaseRequestHandler):

    def __init__(self, request, client_address, server) -> None:
        socketserver.BaseRequestHandler.__init__(
            self, request, client_address, server)

    def handle(self):
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
                raise askTypeNotFoundError(f"No such type {ask['type']}")
        except askTypeNotFoundError as e:
            logging.info(f"No such ask exists: {e}")
            return
        except Exception as e:
            logging.info(f"Could not handle request: {e}")
            logging.info(traceback.format_exc())
            return

    def do_work(self, ask: Dict) -> List:
        func = ask["function"]
        data = ask["array"]

        with multiprocessing.Pool(2) as p:
            results = p.map(func, data)

        return results


class _ThreadedWorkerServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


class Worker:

    def __init__(self, name: str) -> None:
        logging.basicConfig(filename="worker.log",
                            filemode="w",
                            format="%(levelname)s %(asctime)s - %(message)s",
                            level=logging.INFO)
        self.name = name
        self._server = None

        global _master, _id
        _master = None
        _id = None

    def start(self):
        self.__init__(self.name)
        address = ('localhost', 0)
        self._server = _ThreadedWorkerServer(address, _WorkerServer)

        t = threading.Thread(target=self._server.serve_forever)
        t.setDaemon(True)
        t.start()

    def stop(self):
        if self._server is None:
            logging.warning("No server has been started")
            return

        # TODO: notify master
        self._server.shutdown()

    def get_address(self):
        return self._server.server_address  # find out what port we were given

    def connect_to_master(self, ip, port):
        if self._server is None:
            raise Exception("No server has been started")
        connection_message = {"type": NEW_CONNECTION,
                              "name": self.name, "address": self.get_address()}
        send_message(encode_dict(connection_message), (ip, port))
