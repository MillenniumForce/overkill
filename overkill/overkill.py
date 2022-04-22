"""Main module. All user interactions to distribute tasks should use this module.
See the :class:`ClusterCompute` for more details on distributing tasks.
"""

import socket
from typing import Callable, Dict, List, Tuple, Union

from overkill.servers.utils.server_exceptions import NoWorkersError, WorkError
from overkill.servers.utils.server_messaging_standards import (_DISTRIBUTE,
                                                               _FINISHED_TASK,
                                                               _NO_WORKERS_ERROR,
                                                               _WORK_ERROR)
from overkill.servers.utils.utils import _decode_message, _encode_dict, _recv_msg, _socket_send_message


class ClusterCompute:
    """The ClusterCompute class acts as the main interface between the Master server and the user.
    use this class to distribute an array over a cluster of computers given a function.

    :param n_workers: number of workers to use to distribute 
        (array is distributed evenly accross workers)
    :type n_workers: int
    :param master_address: A tuple of (ip, port) e.g. ("localhost", 5555).
        Use the .get_address() class member of the Master class to get the address
    :type master_address: Tuple[str, int]
    """

    def __init__(self, n_workers: int, master_address: Tuple[str, int]) -> None:
        self.n_workers = n_workers
        self.master_address = master_address

    def map(self, function: Callable, array: List) -> Union[None, List]:
        """Distribute array over function using all compute resources

        :param function: Any array with a single argument
        :type function: Callable
        :param array: array to distribute e.g. if Array type is List[int] then function should accept an int
        :type array: List
        :return: Transformed list if no exception has been raised
        :rtype: Union[None, List]
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            connection_message = {
                "type": _DISTRIBUTE,
                "function": function,
                "array": array
            }
            sock.connect(self.master_address)
            _socket_send_message(_encode_dict(connection_message), sock)
            result = _decode_message(_recv_msg(sock))
        return self.__handle_result(result)

    def __handle_result(self, result: Dict) -> List:
        """Handle returned data from master.
        Asssume that communications are with the master exclusively (no malicious users)
        and that only dictionaries are returned. Current implementation assumes a dictionary
        of the form {"type": str, "data": List}

        :param result: dictionary of the form {"type": str, "data": List}
        :type result: Dict
        :return: transformed list from cluster
        :rtype: List
        """
        return_type = result.get("type")
        if return_type == _FINISHED_TASK:
            return result.get("data")
        if return_type == _WORK_ERROR:
            raise WorkError(result.get("error"))
        if return_type == _NO_WORKERS_ERROR:
            raise NoWorkersError("There are no workers connected to master")
