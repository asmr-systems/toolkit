""" Microcontroller Multitool """

import sys

import click

import asmr.mcu
import asmr.logging
from asmr.ansi import color, style


#:::: Logging
#::::::::::::
log = asmr.logging.get_logger()


def _mcu_ls():
    title = "MCU Inventory"
    print(style.bold(color.white_light(title)))
    fmt_name = lambda s : color.green_light(s)
    fmt_manufacturer = lambda s : color.cyan_light(f"[{s}]")
    fmt_plain = lambda s : color.white_light(f"{s}")
    for idx, mcu in enumerate(asmr.mcu.inventory):
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


@click.group("mcu", invoke_without_command=True)
@click.pass_context
def main(ctx):
    """ microcontroller tools. """
    if ctx.invoked_subcommand is None:
        _mcu_ls()


@main.command('ls')
def mcu_ls():
    _mcu_ls()


@main.command('fetch')
@click.argument('mcu_family',
                required=True,
                type=click.Choice([m.normalize_name() for m in asmr.mcu.inventory]))
@click.argument('material',
                default='all',
                type=click.Choice(['all', 'datasheet', 'software']))
@click.option('--force',
              is_flag=True,
              default=False,
              help="ignore cached values of downloaded materials and re-fetch.")
def mcu_fetch(mcu_family, material, force):
    """positional args: <MCU> <MATERIAL>

    MCU is the microcontroller family name.

    MATERIAL is the material to fetch.
    """
    mcu = list(filter(lambda m : m.normalize_name() == mcu_family, asmr.mcu.inventory))[0]
    if material == 'all':
        mcu.fetch()
    elif material == 'datasheet':
        mcu.fetch_datasheet()
    elif material == 'software':
        mcu.fetch_software()
