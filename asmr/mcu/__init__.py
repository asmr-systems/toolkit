""" Tools for micro controller support. """
from .samd11 import SAMD11
from .samd21 import SAMD21


inventory = [
    SAMD11(),
    SAMD21(),
]
