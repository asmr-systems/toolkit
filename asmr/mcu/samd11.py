""" Atmel (Microchip) SAM D11 """

import dataclasses
import typing as t

from .base import Mcu, Core
from asmr.mcu.cores import ARM_Cortex_M0Plus


@dataclasses.dataclass
class SAMD11(Mcu):
    family: str              = 'SAMD11'
    name: str                = 'SAMD11xxxx'
    cpu: Core                = ARM_Cortex_M0Plus
    gcc_defines: t.List[str] = []
    cmsis_device_header: str = 'samd11.h'
    sources: t.List[str]     = []
    linker_script: str       = '???'
    bootloader: str          = 'uf2-samdx1'
    bootloader_build: str    = 'build/asmr_systems'
    manufacturer: str        = 'Atmel'
    datasheet_url: str       = 'http://ww1.microchip.com/downloads/en/devicedoc/atmel-42363-sam-d11_datasheet.pdf'
    software_url: str        = 'https://ww1.microchip.com/downloads/en/DeviceDoc/ASF3.51.0_StandalonePackage.zip'

    def fetch_software(self, use_cached=True):
        print("FETCHING SOFT")
