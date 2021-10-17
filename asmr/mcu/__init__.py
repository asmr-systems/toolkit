""" Tools for micro controller support. """
from .samd11 import SAMD11
from .samd21 import SAMD21
from .stm32f4 import STM32F405


inventory = [
    SAMD11(),
    SAMD21(),
    STM32F405(),
]

def ls():
    import sys
    from asmr.ansi import color, style

    title = "MCU Inventory"
    print(style.bold(color.white_light(title)))
    fmt_name = lambda s : color.green_light(s)
    fmt_manufacturer = lambda s : color.cyan_light(f"[{s}]")
    fmt_plain = lambda s : color.white_light(f"{s}")
    for idx, mcu in enumerate(inventory):
        sys.stdout.write(f"{idx})  ")
        sys.stdout.write(f"{fmt_name(mcu.normalize_name())} ")
        sys.stdout.write(f"{fmt_manufacturer(mcu.manufacturer)} ")
        sys.stdout.write(fmt_plain("("))
        sys.stdout.write(fmt_plain(mcu.cpu.arch) + " ")
        sys.stdout.write(fmt_plain(mcu.cpu.name) + ", ")
        sys.stdout.write(f"{fmt_plain(mcu.cpu.bits)}-bit, ")
        sys.stdout.write(f"{fmt_plain(mcu.cpu.clock_mhz)}MHz, ")
        sys.stdout.write(f"support_software={color.green('yes') if mcu.software_url else color.red('no')}")
        print(fmt_plain(")"))
