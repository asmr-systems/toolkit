""" Atmel (Microchip) SAM D21 """

import dataclasses
import pathlib
import shutil

import asmr.fs
from asmr.mcu.cores import ARM_Cortex_M0Plus

from .base import Mcu, Core
from .utils import extract_mcu_from_asf


@dataclasses.dataclass
class SAMD21(Mcu):
    family: str         = 'SAMD21'
    name: str           = 'SAMD21G18A'
    cpu: Core           = ARM_Cortex_M0Plus
    linker_script: str  = 'samd21g18a_flash.ld'
    startup_source: str = 'startup_samd21.c'
    manufacturer: str   = 'Atmel'
    datasheet_url: str  = 'https://ww1.microchip.com/downloads/en/DeviceDoc/SAM_D21_DA1_Family_DataSheet_DS40001882F.pdf'
    software_url: str   = 'https://ww1.microchip.com/downloads/en/DeviceDoc/ASF3.51.0_StandalonePackage.zip'

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
        #::::::::::::::::::::::::
        device_root = cwd/f"cmsis/device/{self.normalize_name()}"
        device_root.mkdir(parents=True, exist_ok=True)

        shutil.copytree(root/f"sam0/utils/cmsis/{self.normalize_name()}/include/",
                        device_root/'include',
                        dirs_exist_ok=True)
        shutil.copytree(root/f"sam0/utils/cmsis/{self.normalize_name()}/source/",
                        device_root/'src',
                        dirs_exist_ok=True)


        #:::: Fetch Linker Scripts
        #:::::::::::::::::::::::::
        linker_root = cwd/f"linkers/{self.normalize_name()}"
        linker_root.mkdir(parents=True, exist_ok=True)

        shutil.copytree(root/f"sam0/utils/linker_scripts/{self.normalize_name()}/gcc/",
                        linker_root,
                        dirs_exist_ok=True)

        #:::: Fetch Bootloader
        #:::::::::::::::::::::
        bootloader_url = 'https://github.com/asmr-systems/uf2-samdx1'
        root = cache/pathlib.Path(pathlib.Path(bootloader_url.split("/")[-1]).stem)

        if root.exists():
            with asmr.fs.pushd(root):
                asmr.git.pull(branch='master')
        else:
            asmr.git.clone(bootloader_url, root)

        bootloader_root = cwd/f"bootloaders/{self.normalize_name()}"
        bootloader_root.mkdir(parents=True, exist_ok=True)

        shutil.copytree(root, bootloader_root, dirs_exist_ok=True)
        shutil.rmtree(bootloader_root/'.git')
