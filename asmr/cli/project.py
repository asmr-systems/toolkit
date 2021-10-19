""" Project Tools """

import os
import pathlib
import shutil

import click
import jinja2

import asmr.fs
import asmr.git
import asmr.logging
import asmr.mcu
import asmr.software


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
    asmr.mcu.ls()
    selected_idx = int(click.prompt(f"select microcontroller {list(range(len(mcu_idx)))}"))
    while not click.confirm(f"selected '{mcu_idx[selected_idx]}'. continue?"):
        asmr.mcu.ls()
        selected_idx = int(click.prompt(f"select microcontroller {list(range(len(mcu_idx)))}"))

    mcu = asmr.mcu.inventory[selected_idx]
    print(f"selected {mcu.name}")

    log.info(f"==== Initializing '{project_name}' ====")

    # TODO un-comment this!
    #asmr.software.update()

    template_path = asmr.fs.home()/"module-template"

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

        # configure
        config_path = pathlib.Path(asmr.fs.project_config_filename)
        with open(config_path, 'w+') as fd:
            fd.write(f"[project]\n")
            fd.write(f"name={project_name}\n")
            fd.write(f"mcu={mcu.name}\n")

        #:::: Render Templates
        #:::::::::::::::::::::
        context = {
            'project_name': project_name,
            'cpu_cmsis_name': mcu.cpu.cmsis_name,
            'cpu_float_abi': 'hard' if mcu.cpu.fpu else 'soft',
            'mcu_family': mcu.normalize_family(),
            'mcu_full_name': mcu.normalize_name(),
            'mcu_startup_src': mcu.startup_source,
            'mcu_linker_script': mcu.linker_script,
            'bootloader_path': mcu.bootloader_path,
        }
        templates = [
            'README.md.jinja',
            'firmware/Makefile.jinja',
        ]
        for template in templates:
            with open(template, 'r') as fd:
                t = jinja2.Template(fd.read())
            t.stream(**context).dump(template.split('.jinja')[0])
            os.remove(template)

    log.info(f"==== Successfully Initialized '{project_name}' ====")
    log.info("")
    log.info(f"To begin developing, run:")
    log.info(f"   cd {project_name}")
    log.info(f"   asmr develop")
