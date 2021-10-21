""" Available CPUs """

from dataclasses import dataclass

from .base import Core


@dataclass
class ARM_Cortex_M0Plus(Core):
    name: str        = "Cortex-M0+"
    cmsis_name: str  = "cm0plus"
    gcc_name: str    = "cortex-m0plus"
    arch: str        = "ARM"
    bits: int        = 32
    clock_mhz: float = 48
    fpu: bool        = False


@dataclass
class ARM_Cortex_M4(Core):
    name: str        = "Cortex-M4"
    cmsis_name: str  = "cm4"
    gcc_name: str    = "cortex-m4"
    arch: str        = "ARM"
    bits: int        = 32
    clock_mhz: float = 48
    fpu: bool        = True
