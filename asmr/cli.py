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
import asmr.vagrant
from asmr.ansi import color, style


log = asmr.logging.get_logger()


@click.group(help="ASMR Labs command-line tool.")
@click.version_option()
def main():
    """ cli entrypoint """
    pass


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


@main.command('init')
def project_init():
    # git clone template into cache or pull from main
    template_path = asmr.fs.cache()/"module-template"
    if (template_path).exists():
        with asmr.fs.pushd(template_path):
            asmr.git.pull("main")
    else:
        url = "https://github.com/asmr-systems/module-template.git"
        asmr.git.clone(url, template_path)

    # ask for new project name
    project_name = click.prompt("project name").replace(' ', '-')
    while not click.confirm(f"project name is '{project_name}'. continue?"):
        project_name = click.prompt("project name").replace(' ', '-')

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

        # add dev-env submodule
        url = "https://github.com/asmr-systems/dev-environment.git"
        asmr.git.add_submodule(url, pathlib.Path('.dev-environ'))

        # add mcu library submodule
        url = "https://github.com/asmr-systems/mcu-library.git"
        asmr.git.add_submodule(url, pathlib.Path('firmware/vendor/libmcu'))

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

    pass


def _start():
    machine_id, state = asmr.vagrant.status()

    if machine_id == None:
        # create it
        # TODO get project root (for now we have to be in project root)
        dev_env_path = pathlib.Path('.dev-environ')
        with asmr.fs.pushd(dev_env_path):
            asmr.vagrant.up()

        # re-read state
        machine_id, state = asmr.vagrant.status()

    if machine_id != None:
        if state == 'saved':
            asmr.vagrant.resume(machine_id)
        elif state == 'poweroff':
            asmr.vagrant.up(machine_id)

    # TODO mount project root into dev env (if not already done)
    asmr.vagrant.mount(machine_id, pathlib.Path.cwd(), "test-project") # TODO use project name.

    # TODO ssh in
    asmr.vagrant.ssh(machine_id)


@main.group(help="dev environ tools", invoke_without_command=True)
@click.pass_context
def develop(ctx):
    if ctx.invoked_subcommand is None:
        _start()  # default command.


@develop.command("status")
def status():
    machine_id, state = asmr.vagrant.status()
    if machine_id == None:
        log.error(f"ASMR development environment does not exit.")
        return
    log.info(f"ASMR development environment ({machine_id}): {state}")


@develop.command("pause")
def dev_pause():
    machine_id, state = asmr.vagrant.status()
    if machine_id != None and state == 'running':
        asmr.vagrant.suspend(machine_id)


@develop.command("stop")
def dev_stop():
    machine_id, state = asmr.vagrant.status()
    if machine_id != None:
        asmr.vagrant.halt(machine_id)


@develop.command("destroy")
def dev_destroy():
    machine_id, state = asmr.vagrant.status()
    if machine_id != None:
        asmr.vagrant.destroy(machine_id)


@develop.command("start")
def dev_start():
    _start()

@main.command('test')
def general_testing():
    pass


if __name__ == '__main__':
    main()
