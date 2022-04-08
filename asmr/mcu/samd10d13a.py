""" Atmel (Microchip) SAMD10D13A """

import dataclasses
import pathlib
import shutil
import typing as t

import asmr.fs
from .base import Mcu, Core
from .samd import SAMD
from asmr.mcu.cores import ARM_Cortex_M0Plus


@dataclasses.dataclass
class SAMD10D13A(SAMD):
    name: str                = 'SAMD10D13A'
    cpu: Core                = ARM_Cortex_M0Plus
    sources: t.List[str]     = dataclasses.field(default_factory=lambda: ['gcc/startup_samd10.c'])
    gcc_defines: t.List[str] = dataclasses.field(default_factory=lambda: ['__SAMD10D13AM__'])
    cmsis_device_header: str = 'samd10.h'
    linker_script: str       = 'samd10d13am_flash.ld'
    bootloader: str          = '-'
    bootloader_build: str    = '-'
    manufacturer: str        = 'Atmel'
    datasheet_url: str       = 'https://www.mouser.com/datasheet/2/268/atmel-42242-sam-d10_summary-1368819.pdf'
    software_url: str        = 'https://ww1.microchip.com/downloads/en/DeviceDoc/ASF3.51.0_StandalonePackage.zip'

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

        #extract_mcu_from_asf(str(cache/asf_base), self)
        root = cache/asf_base
        cwd = pathlib.Path.cwd()

        #:::: Fetch CMSIS Device Headers
        #:::::::::::::::::::::::::::::::
        device_root = cwd/f"cmsis/device/{self.normalize_family()}"
        device_root.mkdir(parents=True, exist_ok=True)

        shutil.copytree(root/f"sam0/utils/cmsis/{self.normalize_family()}/include/",
                        device_root/'include',
                        dirs_exist_ok=True)
        shutil.copytree(root/f"sam0/utils/cmsis/{self.normalize_family()}/source/",
                        device_root/'src',
                        dirs_exist_ok=True)

        #:::: Fetch Linker Scripts
        #:::::::::::::::::::::::::
        linker_scripts = cwd/f"linkers/{self.normalize_family()}"
        shutil.copytree(root/f"sam0/utils/linker_scripts/{self.normalize_family()}/gcc/",
                        linker_scripts,
                        dirs_exist_ok=True)
