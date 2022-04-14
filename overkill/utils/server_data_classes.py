from dataclasses import dataclass, field
from threading import Event
from typing import Any, List, Tuple


@dataclass
class workerInfo:
    id: str
    name: str
    address: Tuple
    active: bool = True


@dataclass
class masterInfo:
    address: Tuple


@dataclass
class WorkOrder:
    num_workers: int
    event: Event
    data: List = field(default_factory=lambda: [])
    progress: float = 0

    def update(self, new_data: List, order: int):
        self.data.insert(order, new_data)
        self.progress = len(self.data) / self.num_workers
        return self.progress
