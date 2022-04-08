""" SAMD Family Base """

from .base import Mcu

class SAMD(Mcu):
    def family(self):
        return 'SAMD'

    def series(self):
        return self.name[0:6]
