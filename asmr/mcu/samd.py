""" SAMD Family Base """

from .base import Mcu

class SAMD(Mcu):
    rom_address: int = 0x00000000

    def family(self):
        return 'SAMD'

    def series(self):
        return self.name[0:6]
