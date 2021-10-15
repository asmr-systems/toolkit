""" Software tools """

import click

import asmr.software


@click.command("update")
def update():
    """ update software. """
    asmr.software.update()
