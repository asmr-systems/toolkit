""" ASMR Building Toolkit """

import click

import asmr.fs
import asmr.logging
import asmr.process


#:::: Logging
#::::::::::::
log = asmr.logging.get_logger()


#:::: Contants
#:::::::::::::
ProjectFirmwarePath = 'firmware'


@click.group('build', invoke_without_command=True)
@click.pass_context
def main(ctx):
    """ run the project build pipeline. """
    if ctx.invoked_subcommand is None:
        # TODO run entire build pipeline....
        print("building shit left and right.")


@main.command("firmware")
def firmware():
    """ build project firmware. """
    root = asmr.fs.get_project_root()
    if root == None:
        log.error(f"You are not within a project!")
        return

    with asmr.fs.pushd(root/ProjectFirmwarePath):
        asmr.process.run(
            f"make",
            capture=False
        )
