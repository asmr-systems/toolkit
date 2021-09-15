""" Commandline Tool """

import sys

import click

import asmr.mcu


@click.group(help="ASMR Labs command-line tool.")
@click.version_option()
def main():
    """ cli entrypoint """
    pass


# mcu tools

def _mcu_ls():
    title = "microcontroller inventory"
    print(title)
    print('-'*len(title))
    for idx, mcu in enumerate(asmr.mcu.inventory):
        sys.stdout.write(f"{idx})  ")
        sys.stdout.write(f"{mcu.manufacturer} ")
        sys.stdout.write(f"{mcu.name}     ")
        sys.stdout.write(f"(")
        sys.stdout.write(f"{mcu.cpu.arch} ")
        sys.stdout.write(f"{mcu.cpu.name}, ")
        sys.stdout.write(f"{mcu.cpu.bits}-bit, ")
        sys.stdout.write(f"{mcu.cpu.clock_mhz}MHz, ")
        sys.stdout.write(f"support_software={'yes' if mcu.software_url else 'no'}")
        print(")")

@main.group(help="µ-controller tools", invoke_without_command=True)
@click.pass_context
def mcu(ctx):
    if ctx.invoked_subcommand is None:
        _mcu_ls()  # default command.

@mcu.command('ls')
def mcu_ls():
    _mcu_ls()

@mcu.command('fetch')
def mcu_fetch_stuff():
    print("fetching")



if __name__ == '__main__':
    main()
