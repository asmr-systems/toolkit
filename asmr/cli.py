""" Commandline Tool """

import sys
import pathlib
import shutil

import click

import asmr.mcu
import asmr.git
import asmr.http
import asmr.logging
import asmr.string
import asmr.mcli.test # TODO CHANGE THIS
import asmr.mcli.build # TODO CHANGE THIS
import asmr.vagrant
from asmr.ansi import color, style


log = asmr.logging.get_logger()


@click.group(help="ASMR Labs command-line tool.")
@click.version_option()
def main():
    """ cli entrypoint """
    pass


main.add_command(asmr.mcli.test.main)
main.add_command(asmr.mcli.build.main)


# mcu tools

def _mcu_ls():
    title = "MCU Inventory"
    print(style.bold(color.white_light(title)))
    fmt_name = lambda s : color.green_light(s)
    fmt_manufacturer = lambda s : color.cyan_light(f"[{s}]")
    fmt_plain = lambda s : color.white_light(f"{s}")
    for idx, mcu in enumerate(asmr.mcu.inventory):
        sys.stdout.write(f"{idx})  ")
        sys.stdout.write(f"{fmt_name(mcu.normalize_name())} ")
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


@mcu.command('fetch')
@click.argument('mcu_family',
                required=True,
                type=click.Choice([m.normalize_name() for m in asmr.mcu.inventory]))
@click.argument('material',
                default='all',
                type=click.Choice(['all', 'datasheet', 'software']))
@click.option('--force',
              is_flag=True,
              default=False,
              help="ignore cached values of downloaded materials and re-fetch.")
def mcu_fetch(mcu_family, material, force):
    """positional args: <MCU> <MATERIAL>

    MCU is the microcontroller family name.

    MATERIAL is the material to fetch.
    """
    mcu = list(filter(lambda m : m.normalize_name() == mcu_family, asmr.mcu.inventory))[0]
    if material == 'all':
        mcu.fetch()
    elif material == 'datasheet':
        mcu.fetch_datasheet()
    elif material == 'software':
        mcu.fetch_software()


@main.command("update")
def update_software():
    # TODO change to $HOME/.asmr
    # git clone template into cache or pull from main
    template_path = asmr.fs.cache()/"module-template"
    if (template_path).exists():
        with asmr.fs.pushd(template_path):
            asmr.git.pull("main")
    else:
        url = "https://github.com/asmr-systems/module-template.git"
        asmr.git.clone(url, template_path)

    # git clone dev environment into cache or pull from main
    dev_env_path = asmr.fs.cache()/"dev-environment"
    if (dev_env_path).exists():
        with asmr.fs.pushd(dev_env_path):
            asmr.git.pull("main")
    else:
        url = "https://github.com/asmr-systems/dev-environment.git"
        asmr.git.clone(url, dev_env_path)


@main.command('init')
def project_init():
    # ask for new project name
    project_name = click.prompt("project name").replace(' ', '-')
    while not click.confirm(f"project name is '{project_name}'. continue?"):
        project_name = click.prompt("project name").replace(' ', '-')

    # select mcu
    mcu_idx = [m.normalize_name() for m in asmr.mcu.inventory]
    _mcu_ls()
    selected_idx = int(click.prompt(f"select microcontroller {list(range(len(mcu_idx)))}"))
    while not click.confirm(f"selected '{mcu_idx[selected_idx]}'. continue?"):
            _mcu_ls()
            selected_idx = int(click.prompt(f"select microcontroller {list(range(len(mcu_idx)))}"))

    mcu = asmr.mcu.inventory[selected_idx]
    print(f"selected {mcu.name}")

    # TODO do some configuration with this.

    log.info(f"==== Initializing '{project_name}' ====")

    update_software()

    template_path = asmr.fs.cache()/"module-template"

    # create directory here
    repo_path = pathlib.Path('.')/project_name
    shutil.copytree(str(template_path), str(repo_path))

    # remove .git
    shutil.rmtree(str(repo_path/'.git'))

    with asmr.fs.pushd(repo_path):
        # init .git
        asmr.git.init(repo_path)

        # switch to main branch
        asmr.git.branch.rename('main')

        # add mcu library submodule
        url = "https://github.com/asmr-systems/mcu-library.git"
        asmr.git.add_submodule(url, pathlib.Path('firmware/vendor/libmcu'))

    log.info(f"==== Successfully Initialized '{project_name}' ====")
    log.info("")
    log.info(f"To begin developing, run:")
    log.info(f"   cd {project_name}")
    log.info(f"   asmr develop")


@main.command("mount")
@click.argument("dst")
@click.argument("src", required=False)
def mount(dst: str, src: str):
    """ mounts a directory into the running development environment.
    """
    src = pathlib.Path(src) if src != None else pathlib.Path.cwd()
    dst = pathlib.Path(dst)

    if not asmr.vagrant.is_running():
        log.error(f"Development environment not running!")
        return

    asmr.vagrant.mount(src.resolve(), dst)


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


@main.group(help="dev environ tools", invoke_without_command=True)
@click.pass_context
def develop(ctx):
    if ctx.invoked_subcommand is None:
        dev_env_start_and_login()  # default command.


@main.command("dev", help="login to development environment.")
def dev_start():
    dev_env_start_and_login()


@develop.command("status", help="show status of development environment.")
def status():
    machine_id, state = asmr.vagrant.status()
    if machine_id == None:
        log.error(f"development environment does not exit.")
        return
    log.info(f"ASMR development environment ({machine_id}): {state}")


@develop.command("pause", help="suspend the development environment.")
def dev_pause():
    machine_id, state = asmr.vagrant.status()
    if machine_id != None and state == 'running':
        asmr.vagrant.suspend(machine_id)
    else:
        log.info("no development environment to pause, moving on.")


@develop.command("stop", help="shutdown the development environment.")
def dev_stop():
    machine_id, state = asmr.vagrant.status()
    if machine_id != None:
        asmr.vagrant.halt(machine_id)
    else:
        log.info("no development environment to stop, moving on.")


@develop.command("destroy", help="shutdown and delete the development environment.")
def dev_destroy():
    machine_id, state = asmr.vagrant.status()

    prompt = f"this will delete everything in the dev environment, are you sure?"
    if machine_id != None and click.confirm(prompt):
        asmr.vagrant.destroy(machine_id)
    else:
        log.info("no development environment to destroy, moving on.")

@develop.command("provision", help="run provisioning for development environment.")
def dev_provision():
    with asmr.fs.pushd(asmr.fs.cache()/'dev-environment'):
        # provision vm. this could take a few minutes.
        asmr.vagrant.provision()


@main.command('testing')
def general_testing():
    pass


if __name__ == '__main__':
    main()
