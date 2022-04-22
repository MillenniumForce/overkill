
import logging
import socketserver
import traceback
from typing import Dict, List

from overkill.servers.utils.server_data_classes import _MasterInfo
from overkill.servers.utils.server_exceptions import (AskTypeNotFoundError,
                                                      WorkError)
from overkill.servers.utils.server_messaging_standards import (_ACCEPT,
                                                               _ACCEPT_WORK, _CLOSE_CONNECTION,
                                                               _DELEGATE_WORK,
                                                               _REJECT,
                                                               _WORK_ERROR)
from overkill.servers.utils.utils import (_decode_message, _encode_dict,
                                          _recv_msg, _send_message)


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
        data = _recv_msg(self.request)
        try:
            ask = _decode_message(data)
            logging.info(ask)

            if ask["type"] == _REJECT:
                raise Exception("Worker rejected")

            elif ask["type"] == _ACCEPT:
                address = ask["master_address"]
                _master = _MasterInfo(address)
                logging.info(f"Master information: {_master}")
                _id = ask["id"]

            elif ask["type"] == _DELEGATE_WORK:
                results = _do_work(ask)
                _send_message(_encode_dict(
                    {"type": _ACCEPT_WORK, "work_id": ask["work_id"], "data": results, "order": ask["order"]}), _master.address)

            else:
                raise AskTypeNotFoundError(f"No such type {ask['type']}")
                
        except AskTypeNotFoundError as e:
            logging.info(f"No such ask exists: {e}")
            return
        except WorkError as e:
            logging.info(f"Encountered work error: {e}")
            err = {"type": _WORK_ERROR, "work_id": ask["work_id"], "error": e}
            _send_message(_encode_dict(err), _master.address)
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
    if _master:
        msg = _encode_dict({"type": _CLOSE_CONNECTION, "id": _id})
        _send_message(msg, _master.address)
    else:
        logging.info("No master started, skipping closing message")
