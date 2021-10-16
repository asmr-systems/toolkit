""" Helpers """

import glob
import os
import shutil

import asmr.logging

logger = asmr.logging.get_logger()


# TODO REMOVE....THIS IS DEPRECATED.
def extract_mcu_from_asf(root_dir, mcu, force=True):
    core_cmsis = mcu.cpu.cmsis_name
    mcu = mcu.normalize_name()

    mcu_sub_dirs = [
        'linkers',
        'cmsis/core/include',
        'cmsis/device',
    ]

    # deal with a pre-existing mcu directory.
    if os.path.isdir(mcu):
        if force:
            logger.info(f'force removing {mcu} directory')
            shutil.rmtree(mcu)
        else:
            logger.info(f'{mcu} already exists. skipping extraction.')
            return

    # create mcu directories
    for d in map(lambda sd: f'{mcu}/{sd}', mcu_sub_dirs):
        os.makedirs(d)

    # extract linkers -> <mcu>/linkers
    src_linker_dir = f'{root_dir}/sam0/utils/linker_scripts/{mcu}'
    if os.path.isdir(src_linker_dir):
        logger.info(f'extracting linkers to {mcu}/linkers')
        for f in glob.glob(f'{src_linker_dir}/gcc/*.ld'):
            logger.debug(f'creating {mcu}/linkers/{f}')
            shutil.copy(f, f'{mcu}/linkers')
    else:
        logger.debug(f'removing {mcu}/linkers: no linkers available :(')
        os.rmdir(f'{mcu}/linkers')

    # extract cmsis device headers -> <mcu>/cmsis/device/include
    src_cmsis_dev_dir = f'{root_dir}/sam0/utils/cmsis/{mcu}'
    if os.path.isdir(src_cmsis_dev_dir):
        logger.info(f'extracting CMSIS device headers to {mcu}/cmsis/device/include')
        shutil.copytree(f'{src_cmsis_dev_dir}/include', f'{mcu}/cmsis/device/include')
    else:
        logger.debug(f'removing {mcu}/cmsis: no CMSIS device headers available :(')
        shutil.rmtree(f'{mcu}/cmsis')

    # abort if there are no support modules.
    if len(os.listdir(f'{mcu}')) == 0:
        logger.warning(f'unable to get support modules for {mcu}')
        os.rmdir(f'{mcu}')
        return

    # extract cmsis device source files -> <mcu>/cmsis/device/src
    if os.path.isdir(f'{src_cmsis_dev_dir}/source'):
        logger.info(f'extracting CMSIS device sources to {mcu}/cmsis/device/src')
        shutil.copytree(f'{src_cmsis_dev_dir}/source', f'{mcu}/cmsis/device/src')

    # copy relevant cmsis core modules -> <mcu>/cmsis/core
    cmsis_core_dir = f'{root_dir}/thirdparty/CMSIS/Include'
    if f'core_{core_cmsis}.h' in os.listdir(cmsis_core_dir):
        logger.info(f'extracting CMSIS core to {mcu}/cmsis/core/include')
        shutil.copy(f'{cmsis_core_dir}/cmsis_version.h', f'{mcu}/cmsis/core/include')
        shutil.copy(f'{cmsis_core_dir}/cmsis_gcc.h', f'{mcu}/cmsis/core/include')
        shutil.copy(f'{cmsis_core_dir}/cmsis_compiler.h', f'{mcu}/cmsis/core/include')
        shutil.copy(f'{cmsis_core_dir}/core_{core_cmsis}.h', f'{mcu}/cmsis/core/include')
