""" Microcontroller Multitool """
import sys

import click

import asmr.mcu
import asmr.logging
from asmr.ansi import color, style


#:::: Logging
#::::::::::::
log = asmr.logging.get_logger()


@click.group("mcu", invoke_without_command=True)
@click.pass_context
def main(ctx):
    """ microcontroller tools. """
    if ctx.invoked_subcommand is None:
        asmr.mcu.ls()


@main.command('ls')
def mcu_ls():
    asmr.mcu.ls()


@main.command('fetch')
@click.argument('mcu_name',
                required=True,
                type=click.Choice([m.normalize_name() for m in asmr.mcu.inventory]))
@click.argument('material',
                default='all',
                type=click.Choice(['all', 'datasheet', 'software']))
@click.option('--force',
              is_flag=True,
              default=False,
              help="ignore cached values of downloaded materials and re-fetch.")
def mcu_fetch(mcu_name, material, force):
    """positional args: <MCU> <MATERIAL>

    MCU is the microcontroller family name.

    MATERIAL is the material to fetch.
    """
    mcu = list(filter(lambda m : m.normalize_name() == mcu_name, asmr.mcu.inventory))[0]
    if material == 'all':
        mcu.fetch()
    elif material == 'datasheet':
        mcu.fetch_datasheet()
    elif material == 'software':
        mcu.fetch_software()
