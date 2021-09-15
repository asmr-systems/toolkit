""" MCU Base class. """

import abc
from typing import List, Union
from dataclasses import dataclass

@dataclass
class Core(abc.ABC):
    name: str
    arch: str
    bits: int
    clock_mhz: float

@dataclass
class Mcu(abc.ABC):
    name: str
    cpu: Core
    manufacturer: str
    datasheet_url: str
    software_url: Union[str, None]
