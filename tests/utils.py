import socket
from typing import Dict, Tuple
from overkill.utils.server_messaging_standards import _ACCEPT_WORK, _DELEGATE_WORK, _FINISHED_TASK, _NEW_CONNECTION
from overkill.utils.utils import _decode_message, _encode_dict, _send_message


class MockWorker:
    def __init__(self, host: str, port: int) -> None:
        """Mock the functionality of a worker

        :param host: ip of the worker
        :type host: str
        :param port: port of the worker
        :type port: int
        """
        self.address = (host, port)
        self.recieved = None
        self.master_address = None

    def recieve_connection(self) -> None:
        """Revieve a connection from master.
        The recieved message is stored in the MockWorker.response variable

        :raises Exception: no data recieved from master
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            s.bind((self.address))
            s.listen()
            conn, addr = s.accept()
            with conn:
                data = _decode_message(conn.recv(1024))
                print(data)
                if not data:
                    raise Exception("No data recieved from master")
                if data["type"] == _DELEGATE_WORK:
                    result = map(data["function"], data["array"])
                    msg = {
                        "type": _ACCEPT_WORK, "work_id": data["work_id"], "data": result, "order": data["order"]}
                    _send_message(_encode_dict(msg), self.master_address)
                self.recieved = data

    def connect_to_master(self, master_address: Tuple[str, int]) -> None:
        """Send connection request to master

        :param master_address: Tuple of (ip, port)
        :type master_address: Tuple[str, int]
        """
        self.master_address = master_address
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            connection_message = {"type": _NEW_CONNECTION,
                                  "name": "test", "address": self.address}
            sock.connect(master_address)
            sock.sendall(_encode_dict(connection_message))
            print("Sent: {}".format(connection_message))


class MockMaster:
    def __init__(self, host: str = "localhost", port: int = 0) -> None:
        """Mock the functionality of a worker

        :param host: ip of the worker, default to "localhost"
        :type host: str
        :param port: port of the worker, default to 0
        :type port: int
        """
        self.address = (host, port)
        self.recieved = None
        self.master_address = None

    def recieve_connection(self) -> None:
        """Revieve a connection from master.
        The recieved message is stored in the MockWorker.response variable

        :raises Exception: no data recieved from master
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            s.bind((self.address))
            s.listen()
            conn, addr = s.accept()
            with conn:
                data = _decode_message(conn.recv(1024))
                print(data)
                if not data:
                    raise Exception("No data recieved from master")
                msg = _encode_dict({"type": _FINISHED_TASK})
                conn.sendall(msg)
                self.recieved = data
