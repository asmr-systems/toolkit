""" MCU Base class. """

import abc
import dataclasses
import pathlib
import shutil
import typing as t

import asmr.fs
import asmr.logging

log = asmr.logging.get_logger()


@dataclasses.dataclass
class Core(abc.ABC):
    name: str
    cmsis_name: str
    arch: str
    bits: int
    clock_mhz: float

@dataclasses.dataclass
class Mcu(abc.ABC):
    name: str
    cpu: Core
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

    def fetch_datasheet(self, use_cached=True):
        filename = self.datasheet_url.split('/')[-1]
        cache = asmr.fs.cache()

        if not use_cached or not (cache/filename).exists():
            # download
            asmr.http.download_file(self.datasheet_url, cache)

        shutil.copy(cache/filename, pathlib.Path.cwd())
        log.info(f"success fetching {filename}")

    def normalize_name(self):
        return self.name.lower().replace(' ', '')
