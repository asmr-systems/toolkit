""" Available CPUs """

from dataclasses import dataclass

from .base import Core


@dataclass
class ARM_Cortex_MPlus(Core):
    name: str = "Cortex-M0+"
    arch: str = "ARM"
    bits: int = 32
    clock_mhz: float = 48
