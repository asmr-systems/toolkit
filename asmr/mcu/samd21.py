""" Atmel (Microchip) SAM D21 """

import dataclasses
import pathlib
import shutil

import asmr.fs
from asmr.mcu.cores import ARM_Cortex_MPlus

from .base import Mcu, Core
from .utils import extract_mcu_from_asf


@dataclasses.dataclass
class SAMD21(Mcu):
    name: str          = 'SAM D21'
    cpu: Core          = ARM_Cortex_MPlus
    manufacturer: str  = 'Atmel'
    datasheet_url: str = 'https://ww1.microchip.com/downloads/en/DeviceDoc/SAM_D21_DA1_Family_DataSheet_DS40001882F.pdf'
    software_url: str  = 'https://ww1.microchip.com/downloads/en/DeviceDoc/ASF3.51.0_StandalonePackage.zip'

    def fetch_software(self, use_cached=True):
        filename = self.software_url.split("/")[-1]
        cache    = asmr.fs.cache()

        if not use_cached or not (cache/filename).exists():
            # download.
            asmr.http.download_file(self.software_url, cache)

        # unzip software bundle
        unzipped_base = asmr.fs.unzip(cache/filename, cache)[0]

        # unzip inner sofware bundle
        inner_zip_name = list((cache/unzipped_base).glob('*.zip'))[0]
        asf_base = asmr.fs.unzip(inner_zip_name, cache)[0]

        extract_mcu_from_asf(str(cache/asf_base), self)
