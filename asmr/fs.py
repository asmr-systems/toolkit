""" Filesystem utilities. """

import contextlib
import os
import pathlib
import time
import typing as t
import zipfile

from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler

import asmr.env
import asmr.logging


#:::: Logging
#::::::::::::
log = asmr.logging.get_logger()
log.set_level(asmr.logging.Level.debug)


#:::: Constants
#::::::::::::::
_default_cache_dir = '.cache'
_home_dir = os.getenv(asmr.env.home) or pathlib.Path.home()/'.asmr.d/'


@contextlib.contextmanager
def pushd(nwd: pathlib.Path) -> t.Iterator[pathlib.Path]:
    """ Just like bash pushd, but a python context. """
    cwd = pathlib.Path.cwd()
    try:
        yield os.chdir(nwd)
    finally:
        os.chdir(cwd)


# TODO rename this to 'path'?
def home() -> pathlib.Path:
    """ creates the asmr home directory if it doesn't exist. """
    path=pathlib.Path(_home_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


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


class FileSystemWatcher(FileSystemEventHandler):
    """ FileSystem Handler for monitoring changes.

    Since we need to be able to reliably watch the filesystem
    on the host and also within a virtual machine, we don't use
    the Linux inotify system, but polling via the watchdog lib.

    Thanks Michael Cho!
    (https://michaelcho.me/article/using-pythons-watchdog-to-monitor-changes-to-a-directory)
    """

    def __init__(self, ignore: t.List[pathlib.Path]=[]):
        super()
        self.ignore = ignore
        self.events = []


    def __call__(self):
        """ event generator. """
        while True:
            while len(self.events) == 0:
                time.sleep(0.3)

            while len(self.events) != 0:
                event = self.events.pop()
                yield event


    def on_any_event(self, event):
        if event.is_directory:
            return None

        valid_event_types = ['created', 'modified']

        for ignore in self.ignore:
            if str(ignore) in event.src_path:
                return None

        if event.event_type in valid_event_types:
            # TODO mutex?
            self.events.append(event.src_path)


def watch(paths: pathlib.Path,
          ignore: t.List[pathlib.Path]=[]) -> t.Iterator[pathlib.Path]:
    """ watch directories and file. """
    event_handler = FileSystemWatcher(ignore)
    observer = PollingObserver()
    for path in paths:
        observer.schedule(event_handler, str(path), recursive=True)
    observer.start()
    try:
        yield from event_handler()
    finally:
        observer.stop()
        observer.join()
