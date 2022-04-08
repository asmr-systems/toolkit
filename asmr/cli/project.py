""" Project Tools """

import os
import pathlib
import shutil

import click
import jinja2
import toml

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


def jinja_ctx_from_mcu(project_name, mcu):
        return {
            'project_name': project_name,
            'cpu_cmsis_name': mcu.cpu.cmsis_name,
            'cpu_gcc_name': mcu.cpu.gcc_name,
            'cpu_float_abi': 'hard' if mcu.cpu.fpu else 'soft',
            'mcu_family': mcu.normalize_family(),
            'mcu_series': mcu.normalize_series(),
            'mcu_full_name': mcu.normalize_name(),
            'mcu_cmsis_device_header': mcu.cmsis_device_header,
            'mcu_defines': mcu.gcc_defines,
            'mcu_sources': mcu.sources,
            'mcu_linker_script': mcu.linker_script,
            'mcu_bootloader': mcu.bootloader,
            'mcu_bootloader_build': mcu.bootloader_build,
            'compatible_libraries': [d.stem for d in (asmr.fs.get_project_root()/"firmware"/"vendor"/"libasmr"/"libraries").iterdir()],
            'libasmr_srcs': [d.relative_to(asmr.fs.get_project_root()/"firmware"/"vendor") for d in (asmr.fs.get_project_root()/"firmware"/"vendor"/"libasmr").rglob('*.c')] + [d.relative_to(asmr.fs.get_project_root()/"firmware"/"vendor") for d in (asmr.fs.get_project_root()/"firmware"/"vendor"/"libasmr").rglob('*.cc')],
            'bin_path': f'build/{project_name}.bin',
            'rom_addr': mcu.rom_address,
            'mcu_jlink_target': mcu.jlink_target,
        }


def render_template(template, context):
    with open(template, 'r') as fd:
        t = jinja2.Template(fd.read())
    t.stream(**context).dump(str(template.parent/template.stem))
    os.remove(template)


@click.command('build-system')
def update_build_system():
    project_root = asmr.fs.get_project_root()

    # read project.toml from project root
    project_properties = toml.load(project_root/"project.asmr.toml")

    # get mcu being used
    mcu = None
    for m in asmr.mcu.inventory:
        if m.name == project_properties['project']['mcu']:
            mcu = m
            break

    if mcu == None:
        print(f"Microcontroller '{project_properties['project']['mcu']}' is not supported!")
        return

    # get the context from the mcu
    context = jinja_ctx_from_mcu(project_properties['project']['name'], mcu)

    #:::: Update Makefile
    #::::::::::::::::::::

    # remove old Makefile
    os.remove(project_root/"firmware/Makefile")

    # copy over Makefile template
    template_path = shutil.copyfile(asmr.fs.home()/"module-template/firmware/Makefile.jinja",
                                    project_root/"firmware/Makefile.jinja")

    # render jinja template
    render_template(project_root/"firmware/Makefile.jinja", context)

    #:::: Update JLink Flash Script
    #::::::::::::::::::::::::::::::

    # remove old jlink file
    os.remove(project_root/"firmware/flash.jlink")

    # copy over Jlink Flash template
    template_path = shutil.copyfile(asmr.fs.home()/"module-template/firmware/flash.jlink.jinja",
                                    project_root/"firmware/flash.jlink.jinja")

    # render jinja template
    render_template(project_root/"firmware/flash.jlink.jinja", context)

    return


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

    asmr.software.update()

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
        url = "https://github.com/asmr-systems/mcu-support.git"
        asmr.git.add_submodule(url, pathlib.Path('firmware/vendor/'))
        # add libasmr submodule
        url = "https://github.com/asmr-systems/libasmr.git"
        asmr.git.add_submodule(url, pathlib.Path('firmware/vendor/'))
        # non-recursively pull submodules
        asmr.git.pull_submodules(capture_output=False, recursive=False)

        if click.confirm(f"include bootloaders?", default=False):
            asmr.git.pull_submodules(pathlib.Path('firmware/vendor/mcu-support'),
                                     capture_output=False)

        # configure
        config_path = pathlib.Path(asmr.fs.project_config_filename)
        with open(config_path, 'w+') as fd:
            fd.write(f"[project]\n")
            fd.write(f"name=\"{project_name}\"\n")
            fd.write(f"mcu=\"{mcu.name}\"\n")

        #:::: Render Templates
        #:::::::::::::::::::::
        context = jinja_ctx_from_mcu(project_name, mcu)
        templates = [
            pathlib.Path('README.md.jinja'),
            pathlib.Path('firmware/Makefile.jinja'),
            pathlib.Path('firmware/src/main.cc.jinja'),
        ]
        for template in templates:
            render_template(template, context)

    log.info(f"==== Successfully Initialized '{project_name}' ====")
    log.info("")
    log.info(f"To begin developing, run:")
    log.info(f"   cd {project_name}")
    log.info(f"   asmr develop")
