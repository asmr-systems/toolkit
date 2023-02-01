""" Visa Instrument Base Class """

import pyvisa

import asmr.logging


#:::: Logging
#::::::::::::
log = asmr.logging.get_logger()


# singleton VISA resource manager.
class ResourceManager(pyvisa.ResourceManager):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super().__new__(cls)
        return cls.instance


class Instrument:
    timeout_ms = 2000

    def __init__(self, id):
        self.connect(id)

    def connect(self, id: str):
        resource_manager = ResourceManager()
        try:
            self.resource = resource_manager.open_resource(id)
        except pyvisa.errors.VisaIOError as e:
            raise RuntimeError(
                f"Unable to connect to {self.__class__.__name__} ({self.id})"
            ) from e

        self.resource.timeout = self.timeout_ms

        success = False
        while not success:
            try:
                log.info(f"Connected -> {self.resource.query('*IDN?')}")
                success = True
            except pyvisa.errors.VisaIOError as e:
                log.debug("Retrying...")

    @staticmethod
    def list():
        resource_manager = ResourceManager()
        log.info(f"Available Instruments: {resource_manager.list_resources()}")
