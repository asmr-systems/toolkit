""" Software tools """

import click

import asmr.fs
import asmr.git


@click.command("update")
def update():
    """ update software. """
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
