""" Tools for micro controller support. """
from .samd11 import SAMD11
from .samd21 import SAMD21
from .stm32f4 import STM32F405


inventory = [
    SAMD11(),
    SAMD21(),
    STM32F405(),
]
