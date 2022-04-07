""" Software tools """

import click

import asmr.software


@click.command("software")
def update():
    """ update software. """
    asmr.software.update()
