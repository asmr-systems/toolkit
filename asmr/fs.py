""" Filesystem utilities. """

import contextlib
import os
import pathlib
import typing as t
import zipfile

import asmr.env
import asmr.logging

_default_cache_dir = os.getenv(asmr.env.cache) or '.cache'

log = asmr.logging.get_logger()


@contextlib.contextmanager
def pushd(nwd: pathlib.Path) -> t.Iterator[pathlib.Path]:
    """ Just like bash pushd, but a python context. """
    cwd = pathlib.Path.cwd()
    try:
        yield os.chdir(nwd)
    finally:
        os.chdir(cwd)


def cache(path=pathlib.Path(_default_cache_dir)) -> pathlib.Path:
    """ creates the cache if it doesn't exist. """
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_project_root(cwd: pathlib.Path=None) -> pathlib.Path:
    """ searches for project root. """
    if cwd == None:
        cwd = pathlib.Path.cwd()

    if (cwd/'.asmr').exists():
        return cwd

    if cwd.parent == cwd:
        # no project root.
        return None

    return get_project_root(cwd.parent)


def unzip(src: pathlib.Path, dst: pathlib.Path) -> t.List[pathlib.Path]:
    """ extracts zip and returns unzipped dir. """
    unzipped_dirs = set()
    with zipfile.ZipFile(src, 'r') as zdir:
        total_files = len(zdir.namelist())
        total       = f"% {total_files} total"
        unzipped_files = 0
        with log.progress(f"unzipping {src.name}", end_suffix=total) as progress:
            for zfile in zdir.namelist():
                zdir.extract(member=zfile, path=dst)

                unzipped_files+=1
                unzipped_dirs.add(zfile.split('/')[0])
                percent = unzipped_files/total_files
                fn      = zfile.split('/')[-1]
                suffix  = f"{(percent*100):.2f}% {fn[:20]:>20}..."
                progress(percent, suffix=suffix)

    return list(unzipped_dirs)


# Thanks Fred Cirera & Sridhar Ratnakumar! see https://stackoverflow.com/a/1094933
def sizeof_fmt(bs: int, suffix='B') -> str:
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(bs) < 1024.0:
            return f"{bs:3.1f}{unit}{suffix}"
        bs /= 1024.0
    return f"{bs:.1f}Yi{suffix}"
