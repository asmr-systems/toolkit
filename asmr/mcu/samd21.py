""" Atmel (Microchip) SAM D21 """

import dataclasses
import pathlib
import shutil
import typing as t

import asmr.fs
from asmr.mcu.cores import ARM_Cortex_M0Plus

from .base import Mcu, Core
from .samd import SAMD
from .utils import extract_mcu_from_asf


@dataclasses.dataclass
class SAMD21(SAMD):
    name: str                = 'SAMD21G18A'
    cpu: Core                = ARM_Cortex_M0Plus
    rom_address: int         = 0x00000000
    sources: t.List[str]     = dataclasses.field(default_factory=lambda: ['gcc/startup_samd21.c'])
    gcc_defines: t.List[str] = dataclasses.field(default_factory=lambda: ['-D__SAMD21G18A__'])
    cmsis_device_header: str = 'samd21.h'
    linker_script: str       = 'samd21g18a_flash.ld'
    bootloader: str          = 'uf2-samdx1'
    bootloader_build: str    = 'build/asmr_systems'
    manufacturer: str        = 'Atmel'
    jlink_target: str        = 'ATSAMD21G18A'
    datasheet_url: str       = 'https://ww1.microchip.com/downloads/en/DeviceDoc/SAM_D21_DA1_Family_DataSheet_DS40001882F.pdf'
    software_url: str        = 'https://ww1.microchip.com/downloads/en/DeviceDoc/ASF3.51.0_StandalonePackage.zip'

    def family():
        return 'SAMD'

    def series():
        return 'SAMD21'

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
        linker_root = cwd/f"linkers/{self.normalize_family()}"
        linker_root.mkdir(parents=True, exist_ok=True)

        shutil.copytree(root/f"sam0/utils/linker_scripts/{self.normalize_family()}/gcc/",
                        linker_root,
                        dirs_exist_ok=True)

        #:::: Fetch Bootloader
        #:::::::::::::::::::::
        bootloader_url = 'https://github.com/asmr-systems/uf2-samdx1.git'

        bootloaders_dir = cwd/"bootloaders"
        bootloaders_dir.mkdir(parents=True, exist_ok=True)

        asmr.git.add_submodule(bootloader_url, bootloaders_dir)
