""" Software utilities. """

import asmr.fs
import asmr.git


def update():
    """ update all software. """
    update_toolkit()
    update_dev_environment()
    update_module_template()


def update_toolkit():
    """ TODO. """
    pass


def update_dev_environment():
    # git clone dev environment into asmr home or pull from main
    dev_env_path = asmr.fs.home()/"dev-environment"
    if (dev_env_path).exists():
        with asmr.fs.pushd(dev_env_path):
            asmr.git.pull("main")
    else:
        url = "https://github.com/asmr-systems/dev-environment.git"
        asmr.git.clone(url, dev_env_path)


def update_module_template():
    # git clone module template into asmr home or pull from main
    template_path = asmr.fs.home()/"module-template"
    if (template_path).exists():
        with asmr.fs.pushd(template_path):
            asmr.git.pull("main")
    else:
        url = "https://github.com/asmr-systems/module-template.git"
        asmr.git.clone(url, template_path)
