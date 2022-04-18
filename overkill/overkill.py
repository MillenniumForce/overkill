"""Main module."""

import socket
from typing import Callable, Dict, List, Tuple

from overkill.utils import server_messaging_standards, utils


class ClusterCompute:

    def __init__(self, n_workers: int, master_address: Tuple[str, int]) -> None:
        self.n_workers = n_workers
        self.master_address = master_address

    def map(self, function: Callable, array: List):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            connection_message = {
                "type": server_messaging_standards.DISTRIBUTE,
                "function": function,
                "array": array
            }
            sock.connect(self.master_address)
            sock.sendall(utils.encode_dict(connection_message))
            result = utils.decode_message(sock.recv(10000))
        return self.__handleResult(result)

    def __handleResult(self, result: Dict):
        return_type = result.get("type")
        if return_type == server_messaging_standards.FINISHED_TASK:
            return result.get("data")
