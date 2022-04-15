"""Experimental module, WIP"""

from dataclasses import dataclass
from typing import Callable, List
from overkill.utils.server_messaging_standards import DISTRIBUTE, NEW_CONNECTION


@dataclass(frozen=True)
class ask_distribute:
    function: Callable
    array: List
    type: str = DISTRIBUTE


@dataclass(frozen=True)
class ask_new_connection:
    name: str
    type: str = NEW_CONNECTION
