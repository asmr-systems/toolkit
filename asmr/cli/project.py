""" Project Tools """

import pathlib
import shutil

import click

import asmr.fs
import asmr.git
import asmr.logging
import asmr.mcu

import asmr.cli.software


#:::: initialize logger.
log = asmr.logging.get_logger()


@click.group("new", help="create new projects.")
def new():
    pass


@new.command("project", help="create a new project.")
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

    software.update()

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
