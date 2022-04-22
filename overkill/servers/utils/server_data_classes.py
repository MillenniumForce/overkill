"""Module stores information about the servers"""

from dataclasses import dataclass, field
from threading import Event
from typing import Any, List, Tuple, Union

from overkill.servers.utils.server_exceptions import WorkError


@dataclass
class _WorkerInfo:
    """Worker inforamtion class"""
    id: str
    name: str
    address: Tuple
    can_accept_work: bool = True


@dataclass
class _MasterInfo:
    """Master information class"""
    address: Tuple


@dataclass
class _WorkOrder:
    """Class documents information about a work order from a client"""
    num_workers: int
    event: Event
    data: List = field(default_factory=lambda: [])
    progress: float = 0
    error: Union[None, WorkError] = None

    def update(self, new_data: List, order: int) -> float:
        """Update the work order given new data

        :param new_data: array of new data
        :type new_data: List
        :param order: order in the original list (i.e where to insert)
        :type order: int
        :return: Progress of the order between 0-1 where 1 is completely done
        :rtype: float
        """
        self.data.insert(order, new_data)
        self.progress = len(self.data) / self.num_workers
        return self.progress
