"""Experimental module, WIP"""

from dataclasses import dataclass
from typing import Callable, List
from overkill.servers.utils.server_messaging_standards import _DISTRIBUTE, _NEW_CONNECTION


@dataclass(frozen=True)
class ask_distribute:
    function: Callable
    array: List
    type: str = _DISTRIBUTE


@dataclass(frozen=True)
class ask_new_connection:
    name: str
    type: str = _NEW_CONNECTION
