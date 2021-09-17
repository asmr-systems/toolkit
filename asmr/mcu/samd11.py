""" Atmel (Microchip) SAM D11 """

import dataclasses

from .base import Mcu, Core
from asmr.mcu.cores import ARM_Cortex_MPlus


@dataclasses.dataclass
class SAMD11(Mcu):
    name: str          = 'SAM D11'
    cpu: Core          = ARM_Cortex_MPlus
    manufacturer: str  = 'Atmel'
    datasheet_url: str ='http://ww1.microchip.com/downloads/en/devicedoc/atmel-42363-sam-d11_datasheet.pdf'
    software_url: str  ='https://ww1.microchip.com/downloads/en/DeviceDoc/ASF3.51.0_StandalonePackage.zip'

    def fetch_software(self, use_cached=True):
        print("FETCHING SOFT")
