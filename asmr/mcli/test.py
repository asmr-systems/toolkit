""" ASMR Testing Toolkit """

import pathlib

import click

import asmr.fs
import asmr.logging
import asmr.process


#:::: Logging
#::::::::::::
log = asmr.logging.get_logger()


#:::: Contants
#:::::::::::::
ProjectFirmwareUnitTestPath = pathlib.Path('firmware/tests/unit')


@click.group('test', invoke_without_command=True)
@click.pass_context
def main(ctx):
    """ testing multitool. """
    if ctx.invoked_subcommand is None:
        print("HOWDY FUCKERsssssaaaaaaasANANANBABABA")


@main.command("unit")
@click.option('-watch',
              is_flag=True,
              default=False,
              help="rerun tests on source change.")
def unit_test(watch):
    root = asmr.fs.get_project_root()
    if root == None:
        log.error(f"You are not within a project!")
        return

    with asmr.fs.pushd(root/ProjectFirmwareUnitTestPath):
        asmr.process.run(
            f"make",
            capture=False
        )

        if watch:
            for fn in asmr.fs.watch(root/ProjectFirmwareUnitTestPath):
                print(fn)
                # asmr.process.run(
                #     f"make",
                #     capture=False
                # )
