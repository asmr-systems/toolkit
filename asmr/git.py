""" Git utilities. """

import enum
import pathlib

import asmr.fs
import asmr.process


def clone(url: str, dst: pathlib.Path):
    cmd = ['git', 'clone', url, dst]
    ret = asmr.process.run(cmd, stderr_to_stdout=True)

def pull(branch: str="main", remote="origin"):
    cmd = ['git', 'pull', remote, branch]
    ret = asmr.process.run(cmd, stderr_to_stdout=True)

def init(repo_path: pathlib.Path):
    cmd = ['git', 'init']
    ret = asmr.process.run(cmd, stderr_to_stdout=True)

def add_submodule(url: str, dst: pathlib.Path):
    with asmr.fs.pushd(dst):
        cmd = ['git', 'submodule', 'add', url]
        ret = asmr.process.run(cmd, stderr_to_stdout=True)

def pull_submodules(repo_path: pathlib.Path = pathlib.Path('.'),
                    submodules=None,
                    capture_output=True,
                    recursive=True):
    with asmr.fs.pushd(repo_path):
        if submodules == None:
            # default behavior, pull all submodules recursively
            cmd = ['git', 'submodule', 'update', '--init']
            if recursive:
                cmd += ['--recursive']
            ret = asmr.process.run(cmd,
                                   stderr_to_stdout=True,
                                   capture=capture_output)
        else:
            # iterate through submodules listed and pull
            for submodule in submodules:
                cmd = ['git', 'submodule', 'update', '--init']
                if recursive:
                    cmd += ['--recursive']
                cmd += [submodule]
                ret = asmr.process.run(cmd,
                                       stderr_to_stdout=True,
                                       capture=capture_output)

def _branch_rename(new: str):
    cmd = ['git', 'branch', '-m', new]
    ret = asmr.process.run(cmd, stderr_to_stdout=False)

class branch(enum.Enum):
    rename = _branch_rename
