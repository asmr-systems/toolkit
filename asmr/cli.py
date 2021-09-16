""" Commandline Tool """

import sys
import pathlib

import click

import asmr.mcu
import asmr.http
import asmr.logging
import asmr.string
from asmr.ansi import color, style


@click.group(help="ASMR Labs command-line tool.")
@click.version_option()
def main():
    """ cli entrypoint """
    pass


# mcu tools

def _mcu_ls():
    title = "MCU Inventory"
    print(style.bold(color.white_light(title)))
    fmt_name = lambda s : color.green_light(s.lower().replace(' ',''))
    fmt_manufacturer = lambda s : color.cyan_light(f"[{s}]")
    fmt_plain = lambda s : color.white_light(f"{s}")
    for idx, mcu in enumerate(asmr.mcu.inventory):
        sys.stdout.write(f"{idx})  ")
        sys.stdout.write(f"{fmt_name(mcu.name)} ")
        sys.stdout.write(f"{fmt_manufacturer(mcu.manufacturer)} ")
        sys.stdout.write(fmt_plain("("))
        sys.stdout.write(fmt_plain(mcu.cpu.arch) + " ")
        sys.stdout.write(fmt_plain(mcu.cpu.name) + ", ")
        sys.stdout.write(f"{fmt_plain(mcu.cpu.bits)}-bit, ")
        sys.stdout.write(f"{fmt_plain(mcu.cpu.clock_mhz)}MHz, ")
        sys.stdout.write(f"support_software={color.green('yes') if mcu.software_url else color.red('no')}")
        print(fmt_plain(")"))


@main.group(help="µ-controller tools", invoke_without_command=True)
@click.pass_context
def mcu(ctx):
    if ctx.invoked_subcommand is None:
        _mcu_ls()  # default command.


@mcu.command('ls')
def mcu_ls():
    _mcu_ls()

# @click.argument('mcu',
#               required=True,
#               type=click.Choice([m.name.lower().replace(' ','') for m in asmr.mcu.inventory]),
#               help="the microcontroller family name.")
# @click.argument('material',
#               required=True,
#               type=click.Choice(['datasheet', 'software']),
#               help="material to fetch.")
@mcu.command('fetch')
@click.argument('mcu_family',
                required=True,
                type=click.Choice([m.name.lower().replace(' ','') for m in asmr.mcu.inventory]))
@click.argument('material',
                required=True,
                type=click.Choice(['datasheet', 'software']))
@click.option('--force',
              is_flag=True,
              default=False,
              help="ignore cached values of downloaded materials and re-fetch.")
def mcu_fetch(mcu_family, material, force):
    """positional args: <MCU> <MATERIAL>

    MCU is the microcontroller family name.

    MATERIAL is the material to fetch.
    """
    mcu = list(filter(lambda m : m.name.lower().replace(' ', '') == mcu_family, asmr.mcu.inventory))[0]
    url = mcu.datasheet_url if material == "datasheet" else mcu.software_url
    asmr.http.download_file(url, pathlib.Path("."))

@main.command('test')
def general_testing():
    pass

if __name__ == '__main__':
    main()
