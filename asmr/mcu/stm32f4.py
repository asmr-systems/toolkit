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
    name: str          = 'STM32F405'
    cpu: Core          = ARM_Cortex_M4
    manufacturer: str  = 'ST Microelectronics'
    datasheet_url: str = 'https://www.st.com/resource/en/datasheet/dm00037051.pdf'
    software_url: str  = 'https://github.com/STMicroelectronics/cmsis_device_f4.git'

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
            linkers_root = cwd/'linkers/stm32f4'
            linkers_root.mkdir(parents=True, exist_ok=True)
            # TODO download? or something?

            #:::: Fetch Bootloader
            #:::::::::::::::::::::
            bootloader_url = 'https://github.com/adafruit/tinyuf2.git'
            root = pathlib.Path(pathlib.Path(bootloader_url.split("/")[-1]).stem)

            if root.exists():
                with asmr.fs.pushd(root):
                    asmr.git.pull(branch='master')
            else:
                asmr.git.clone(bootloader_url, root)

            bootloader_root = cwd/'bootloaders/stm32f4'
            bootloader_root.mkdir(parents=True, exist_ok=True)

            shutil.copytree(root/'ports/stm32f4/', bootloader_root, dirs_exist_ok=True)
