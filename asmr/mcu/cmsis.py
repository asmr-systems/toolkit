""" CMSIS utilities.  """

import pathlib
import shutil

import asmr.fs
import asmr.git
import asmr.logging


#:::: Logging
#::::::::::::
log = asmr.logging.get_logger()

#:::: Constants
#::::::::::::::
cmsis_repository = 'https://github.com/ARM-software/CMSIS_5.git'


def fetch_core_headers():
    """ fetch cmsis core headers and restructure into current directory. """
    cwd = pathlib.Path.cwd()

    with asmr.fs.pushd(asmr.fs.cache()):
        cmsis_root = pathlib.Path(pathlib.Path(cmsis_repository.split('/')[-1]).stem)

        if cmsis_root.exists():
            with asmr.fs.pushd(cmsis_root):
                asmr.git.pull(branch='develop')
        else:
            asmr.git.clone(cmsis_repository, cmsis_root)

        cmsis_core = cwd/'cmsis/core'
        cmsis_core.mkdir(parents=True, exist_ok=True)
        shutil.copytree(cmsis_root/'CMSIS/Core/Include/',
                        cmsis_core/'include',
                        dirs_exist_ok=True)
        log.info(f"fetched headers and put in 'cmsis' dir")
