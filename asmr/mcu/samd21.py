""" Atmel (Microchip) SAM D21 """

from .base import Mcu, Core
from asmr.mcu.cores import ARM_Cortex_MPlus


class SAMD21(Mcu):
    name: str = 'SAM D21'
    cpu: Core = ARM_Cortex_MPlus
    manufacturer: str = 'Atmel'
    datasheet_url: str = 'https://ww1.microchip.com/downloads/en/DeviceDoc/SAM_D21_DA1_Family_DataSheet_DS40001882F.pdf'
    software_url: str = 'https://ww1.microchip.com/downloads/en/DeviceDoc/ASF3.51.0_StandalonePackage.zip'
