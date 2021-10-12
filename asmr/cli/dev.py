""" Development Multitool """

import pathlib

import click

import asmr.fs
import asmr.logging
import asmr.vagrant


#:::: initialize logger.
log = asmr.logging.get_logger()


def dev_env_create(project_root: pathlib.Path):
    """ create a dev environment virtual machine. """
    with asmr.fs.pushd(asmr.fs.cache()/'dev-environment'):
        # build and provision vm. this could take a few minutes.
        asmr.vagrant.up()


def dev_env_start_and_login():
    """ start, if necessary, and login. """
    host_root = asmr.fs.get_project_root()
    if host_root == None:
        log.error(f"Not within a project! You must be in an ASMR Project!")
        return

    guest_root = pathlib.Path("/asmr/projects")/host_root.name

    log.info(f"starting up dev environment ({host_root.name})...")

    machine_id, state = asmr.vagrant.status()

    if not asmr.vagrant.exists():
        # create it
        dev_env_create(host_root)

        # re-read state
        machine_id, state = asmr.vagrant.status()

    if state == 'saved':
        asmr.vagrant.resume(machine_id)
    elif state == 'poweroff':
        asmr.vagrant.up(machine_id)
        asmr.vagrant.mount(host_root, guest_root)

    asmr.vagrant.mount(host_root, guest_root)
    asmr.vagrant.ssh(machine_id, dest=guest_root)


@click.group("dev", help="dev environ tools", invoke_without_command=True)
@click.pass_context
def main(ctx):
    if ctx.invoked_subcommand is None:
        dev_env_start_and_login()  # default command.


@main.command("status", help="show status of development environment.")
def status():
    machine_id, state = asmr.vagrant.status()
    if machine_id == None:
        log.error(f"development environment does not exit.")
        return
    log.info(f"ASMR development environment ({machine_id}): {state}")


@main.command("pause", help="suspend the development environment.")
def pause():
    machine_id, state = asmr.vagrant.status()
    if machine_id != None and state == 'running':
        asmr.vagrant.suspend(machine_id)
    else:
        log.info("no development environment to pause, moving on.")


@main.command("stop", help="shutdown the development environment.")
def stop():
    machine_id, state = asmr.vagrant.status()
    if machine_id != None:
        asmr.vagrant.halt(machine_id)
    else:
        log.info("no development environment to stop, moving on.")


@main.command("rm", help="shutdown and delete the development environment.")
def rm():
    machine_id, state = asmr.vagrant.status()

    prompt = f"this will delete everything in the dev environment, are you sure?"
    if machine_id != None and click.confirm(prompt):
        asmr.vagrant.destroy(machine_id)
    else:
        log.info("no development environment to destroy, moving on.")


@main.command("provision", help="run provisioning for development environment.")
def provision():
    with asmr.fs.pushd(asmr.fs.cache()/'dev-environment'):
        # provision vm. this could take a few minutes.
        asmr.vagrant.provision()


@main.command("mount")
@click.argument("dst")
@click.argument("src", required=False)
def mount(dst: str, src: str):
    """ mounts a directory into the running development environment."""
    src = pathlib.Path(src) if src != None else pathlib.Path.cwd()
    dst = pathlib.Path(dst)

    if not asmr.vagrant.is_running():
        log.error(f"Development environment not running!")
        return

    asmr.vagrant.mount(src.resolve(), dst)
