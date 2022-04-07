""" Update Tools """

import click

from asmr.cli import software
from asmr.cli import project


@click.group("update", help="update software, makefiles, etc.")
def main():
    pass

main.add_command(software.update)
main.add_command(project.update_makefile)
