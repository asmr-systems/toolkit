""" Oscilloscope Tools """

import sys

from asmr.instruments import Instrument, RigolDS1052E

import click


def plot():
    osc = RigolDS1052E()
    osc.plot()

@click.group("scope", help="oscilloscope tools", invoke_without_command=True)
@click.pass_context
def main(ctx):
    if ctx.invoked_subcommand is None:
        plot()  # default command.

@main.command("log", help="log snapshots from oscilloscope to csv")
@click.argument("filename")
def log(filename: str):
    osc = RigolDS1052E()
    osc.collect(filename, plot=True)
