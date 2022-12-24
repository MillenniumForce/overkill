from typing import Dict, List
from overkill.servers._server_messaging_standards import (FINISHED_TASK,
                                                          NO_WORKERS_ERROR,
                                                          WORK_ERROR)
from overkill.servers._server_exceptions import WorkError, NoWorkersError                                                        


def handle_result(result: Dict) -> List:
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
    if return_type == FINISHED_TASK:
        return result.get("data")
    if return_type == WORK_ERROR:
        raise WorkError(result.get("error"))
    if return_type == NO_WORKERS_ERROR:
        raise NoWorkersError("There are no workers connected to master")

