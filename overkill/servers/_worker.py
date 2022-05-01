
import logging
import socketserver
import traceback
from typing import Dict, List

from overkill.servers._server_data_classes import MasterInfo
from overkill.servers._server_exceptions import AskTypeNotFoundError, WorkError
from overkill.servers._server_messaging_standards import (ACCEPT, ACCEPT_WORK,
                                                          CLOSE_CONNECTION,
                                                          DELEGATE_WORK,
                                                          REJECT, WORK_ERROR)
from overkill.servers._utils import (decode_message, encode_dict, recv_msg,
                                     send_message)

__all__ = [
    "WorkerServer",
    "ThreadedWorkerServer",
    "reset_globals",
    "close_connection_with_master"
]

_master = None  # master info
_id = None  # worker id


class WorkerServer(socketserver.BaseRequestHandler):

    def __init__(self, request, client_address, server) -> None:
        socketserver.BaseRequestHandler.__init__(
            self, request, client_address, server)

    def server_close(self):
        pass

    def handle(self):
        """Handle incoming connections

        :raises Exception: internal error in master server
        :raises askTypeNotFoundError: occurs when there is no case for an ask type
        """
        global _master, _id
        data = recv_msg(self.request)
        try:
            ask = decode_message(data)
            logging.info(ask)

            if ask["type"] == REJECT:
                raise Exception("Worker rejected")

            elif ask["type"] == ACCEPT:
                address = ask["master_address"]
                _master = MasterInfo(address)
                logging.info(f"Master information: {_master}")
                _id = ask["id"]

            elif ask["type"] == DELEGATE_WORK:
                results = _do_work(ask)
                send_message(encode_dict(
                    {"type": ACCEPT_WORK, "work_id": ask["work_id"], "data": results, "order": ask["order"]}), _master.address)

            elif ask["type"] == MASTER_SHUTDOWN:
                _master = None

            else:
                raise AskTypeNotFoundError(f"No such type {ask['type']}")

        except AskTypeNotFoundError as e:
            logging.info(f"No such ask exists: {e}")
            return
        except WorkError as e:
            logging.info(f"Encountered work error: {e}")
            err = {"type": WORK_ERROR, "work_id": ask["work_id"], "error": e}
            send_message(encode_dict(err), _master.address)
        except Exception as e:
            logging.info(f"Could not handle request: {e}")
            logging.info(traceback.format_exc())
            return


def _do_work(ask: Dict) -> List:
    """After recieving work from the master server, execute the function on the data

    :param ask: dict of type, function, array
    :type ask: Dict
    :return: list of computed data
    :rtype: List
    """
    func = ask["function"]
    data = ask["array"]

    try:
        results = list(map(func, data))
    except Exception as e:
        raise WorkError(
            f"Could not compute: {e} \n {traceback.format_exc()}")

    return results


class ThreadedWorkerServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


def reset_globals() -> None:
    """Reset global variables:
    _master, _id
    """
    global _master, _id
    _master = None
    _id = None


def close_connection_with_master() -> None:
    """Close connection with master"""
    try:
        msg = encode_dict({"type": CLOSE_CONNECTION, "id": _id})
        send_message(msg, _master.address)
    except Exception as e:
        logging.info(f"Could not close connection with master, reason: {e}")
