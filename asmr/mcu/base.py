""" MCU Base class. """

import abc
import dataclasses
import pathlib
import shutil
import typing as t

import asmr.fs
import asmr.http
import asmr.logging

log = asmr.logging.get_logger()


@dataclasses.dataclass
class Core(abc.ABC):
    name: str
    cmsis_name: str
    gcc_name: str
    arch: str
    bits: int
    clock_mhz: float
    fpu: bool

@dataclasses.dataclass
class Mcu(abc.ABC):
    name: str
    cpu: Core
    sources: t.List[str]
    gcc_defines: t.List[str]
    cmsis_device_header: str
    linker_script: str
    bootloader: str
    bootloader_build: str
    manufacturer: str
    datasheet_url: str
    software_url: t.Union[str, None]

    def fetch(self, use_cached=True):
        self.fetch_datasheet(use_cached=use_cached)
        self.fetch_software(use_cached=use_cached)

    @abc.abstractmethod
    def fetch_software(self, use_cached=True):
        """ Abstract method for fetching vendor support software. """
        pass

    @abc.abstractmethod
    def family(self):
        """ Abstract method for parsing mcu family from name. """
        pass

    @abc.abstractmethod
    def series(self):
        """ Abstract method for parsing mcu series from name. """
        pass

    def fetch_datasheet(self, use_cached=True):
        filename = self.datasheet_url.split('/')[-1]
        cache = asmr.fs.cache()

        if not use_cached or not (cache/filename).exists():
            # download
            asmr.http.download_file(self.datasheet_url, cache)

        # make datasheets dir
        datasheets_dir = pathlib.Path("datasheets")
        datasheets_dir.mkdir(exist_ok=True)

        shutil.copy(cache/filename, datasheets_dir/f"{self.normalize_family()}.pdf")
        log.info(f"success fetching {filename}")

    def normalize_family(self):
        return self.family().lower().replace(' ', '')

    def normalize_series(self):
        return self.series().lower().replace(' ', '')

    def normalize_name(self):
        return self.name.lower().replace(' ', '')
