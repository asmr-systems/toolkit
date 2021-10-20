""" Atmel (Microchip) SAM D21 """

import dataclasses
import pathlib
import shutil

import asmr.fs
from asmr.mcu.cores import ARM_Cortex_M4

from .base import Mcu, Core
from .utils import extract_mcu_from_asf


@dataclasses.dataclass
class STM32F405(Mcu):
    family: str           = 'STM32F4'
    name: str             = 'STM32F405RG'
    cpu: Core             = ARM_Cortex_M4
    linker_script: str    = 'stm32f405.ld'
    startup_source: str   = 'startup_stm32f405xx.s'
    bootloader: str       = 'tinyuf2/ports/stm32f4'
    bootloader_build: str = '_build/asmr_systems'
    manufacturer: str     = 'ST Microelectronics'
    datasheet_url: str    = 'https://www.st.com/resource/en/datasheet/dm00037051.pdf'
    software_url: str     = 'https://github.com/STMicroelectronics/cmsis_device_f4.git'

    def fetch_software(self, use_cached=True):
        """ fetch cmsis headers, src, linkers, and bootloader for STM32F405. """
        cwd = pathlib.Path.cwd()

        with asmr.fs.pushd(asmr.fs.cache()):
            #:::: Fetch CMSIS Headers
            #::::::::::::::::::::::::
            root = pathlib.Path(pathlib.Path(self.software_url.split("/")[-1]).stem)

            if root.exists():
                with asmr.fs.pushd(root):
                    asmr.git.pull(branch='master')
            else:
                asmr.git.clone(self.software_url, root)

            device_root = cwd/'cmsis/device/stm32f4'
            device_root.mkdir(parents=True, exist_ok=True)

            shutil.copytree(root/'Include/', device_root/'include', dirs_exist_ok=True)
            shutil.copytree(root/'Source/Templates/', device_root/'src', dirs_exist_ok=True)

            #:::: Fetch Linker Script(s)
            #:::::::::::::::::::::::::::
            linker_url = 'https://raw.githubusercontent.com/micropython/micropython/master/ports/bare-arm/stm32f405.ld'

            linkers_root = cwd/'linkers/stm32f4'
            linkers_root.mkdir(parents=True, exist_ok=True)

            asmr.http.download_file(linker_url, linkers_root)

            #:::: Fetch Bootloader
            #:::::::::::::::::::::
            bootloader_url = 'https://github.com/asmr-systems/tinyuf2.git'

            bootloaders_dir = cwd/"bootloaders"
            bootloaders_dir.mkdir(parents=True, exist_ok=True)

            asmr.git.add_submodule(bootloader_url, bootloaders_dir)
