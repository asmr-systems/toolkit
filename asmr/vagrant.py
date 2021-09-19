""" Vagrant utilities. """

import collections
import pathlib
import subprocess

import asmr.process
import asmr.logging

log = asmr.logging.get_logger('asmr::vagrant')


Status = collections.namedtuple('Status', ['id', 'state'])


def status(machine_name: str = "asmr.dev"):
    proc = asmr.process.Pipeline("vagrant global-status --prune", logger=None)
    proc|= f"grep {machine_name}"
    proc|= "awk '{printf \"%s\t%s\",$1,$4}'"
    retcode, stdout, stderr = proc()

    if retcode != 0:
        raise ChildProcessError(stderr)

    if len(stdout) == 0:
        return Status(None, None)

    results = stdout[0].split()

    return Status(results[0], results[1])


def suspend(machine_id: str):
    log.info(f"suspending {machine_id}...")
    asmr.process.run(f"vagrant suspend {machine_id}")


def halt(machine_id: str):
    log.info(f"halting {machine_id}...")
    asmr.process.run(f"vagrant halt {machine_id}")


def destroy(machine_id: str):
    log.info(f"destroying {machine_id}...")
    asmr.process.run(f"vagrant destroy --force {machine_id}")


def up(machine_id: str=None):
    if machine_id:
        log.info(f"starting up {machine_id}...")
        log.info(f"This may take a minute or two...be patient...")
        asmr.process.run(f"vagrant up {machine_id}")
    else:
        log.info(f"Creating ASMR Dev Environment...")
        log.info(f"This will take several minutes...please be patient...")
        asmr.process.run(f"vagrant up", capture=False)


def resume(machine_id: str):
    log.info(f"resuming {machine_id}...")
    asmr.process.run(f"vagrant resume {machine_id}")


def ssh(machine_id: str, dst: pathlib.Path = "/asmr/projects"):
    # Thanks sholsapp! see https://www.py4u.net/discuss/224642
    subprocess.call(f"vagrant ssh -c \"cd {dst}\" {machine_id}", shell=True)


def mount(machine_id: str,
          host_src:pathlib.Path,
          share_name: str,
          machine_name="asmr.dev"):
    # first create a transient sharedfolder
    cmd = "VBoxManage sharedfolder"
    cmd+=f" add {machine_name}"
    cmd+=f" --name {share_name}"
    cmd+=f" --hostpath {host_src}"
    cmd+=f" --transient"

    asmr.process.run(cmd)

    # now mount within the guest.
    cmd = f"sudo mount -t vboxsf -o uid=1000,gid=1000 {share_name} /asmr/projects/{share_name}"
    cmd = f"vagrant ssh -c \"{cmd}\" {machine_id}"
    asmr.process.run(cmd)


def reload():
    # reload vagrantfile
    pass


def provision():
    pass
