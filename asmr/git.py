""" Git utilities. """

import enum
import pathlib

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
    cmd = ['git', 'submodule', 'add', url, dst]
    ret = asmr.process.run(cmd, stderr_to_stdout=True)

def pull_submodules():
    cmd = ['git', 'submodule', 'update', '--init']
    ret = asmr.process.run(cmd, stderr_to_stdout=True)

def _branch_rename(new: str):
    cmd = ['git', 'branch', '-m', new]
    ret = asmr.process.run(cmd, stderr_to_stdout=False)

class branch(enum.Enum):
    rename = _branch_rename
