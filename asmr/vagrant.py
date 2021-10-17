""" Vagrant utilities. """

import collections
import pathlib
import subprocess

import asmr.fs
import asmr.process
import asmr.logging
import asmr.decorators


#:::: Logging
#::::::::::::
log = asmr.logging.get_logger('asmr::vagrant')


#::::Constants
#:::::::::::::
DEFAULT_VM_NAME = "asmr.dev"
mountpoint_file = asmr.fs.home()/'mountpoints.conf'


#:::: Types
#::::::::::
Status = collections.namedtuple('Status', ['id', 'state'])


#:::: Vagrant Functions
#::::::::::::::::::::::
def status(machine_name: str = DEFAULT_VM_NAME) -> Status:
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


def is_running(machine_name: str = DEFAULT_VM_NAME) -> bool:
    """ check whether a machine is running. """
    machine_id, state = status(machine_name)
    if machine_id == None or state != "running":
        return False
    return True


def exists(machine_name: str = DEFAULT_VM_NAME) -> bool:
    """ check whether a machine exists. """
    machine_id, _ = status(machine_name)
    return True if machine_id else False


@asmr.decorators.static_variables(name_to_id={})
def get_id(machine_name: str = DEFAULT_VM_NAME) -> str:
    """ get the machine id for the given machine name. """
    M = get_id.name_to_id
    if machine_name not in M or M[machine_name] == None:
        machine_id, _ = status(machine_name)
        M[machine_name] = machine_id
    return M[machine_name]


def record_mountpoint(host_src: pathlib.Path,
                      guest_dst: pathlib.Path,
                      machine_name="asmr.dev"):
    """ records the mount point if not already recorded. """
    # TODO use machine name for multiple vm support.
    records = [f"{host_src}:{guest_dst}"]
    if mountpoint_file.exists():
        with open(mountpoint_file, 'r') as fd:
            records += [l.strip() for l in fd.readlines()]

    with open(mountpoint_file, 'w+') as fd:
        for record in set(records):
            if record != '':
                fd.write(f"{record}\n")


def mount(host_src: pathlib.Path,
          guest_dst: pathlib.Path,
          machine_name="asmr.dev"):
    """ mount a host directory into the guest machine. """

    machine_id = get_id(machine_name)
    share_name = guest_dst.name

    # does the share exist?
    _, stdout, _  = asmr.process.pipeline([
        f"VBoxManage showvminfo {machine_name}",
        f"grep \"Name: '{share_name}'\""
    ], logger=None)

    # create transient folder share if it doesn't exist.
    if len(stdout) == 0:
        # first create a transient sharedfolder
        cmd = "VBoxManage sharedfolder"
        cmd+=f" add {machine_name}"
        cmd+=f" --name {share_name}"
        cmd+=f" --hostpath {host_src}"
        cmd+=f" --transient"

        asmr.process.run(cmd)

    # enable symlinking within sharedfolder
    # Thanks Dominik! (https://stackoverflow.com/a/24353494)
    cmd = "VBoxManage setextradata"
    cmd+=f" {machine_name}"
    cmd+=f" \"VBoxInternal2/SharedFoldersEnableSymlinksCreate/"+f"{share_name}\""
    cmd+=f" 1"
    asmr.process.run(cmd)

    # is the share already mounted?
    _, stdout, _ = asmr.process.run(
        f"VBoxManage guestproperty get {machine_name} /VirtualBox/GuestAdd/SharedFolders/MountDir",
        logger=None
    )

    if len(stdout) == 1 and stdout[0] == "No value set!":
        # now mount within the guest.
        cmd = f"sudo mkdir -p {guest_dst} & sudo chown vagrant {guest_dst}"
        cmd = f"{cmd} & sudo mount -t vboxsf -o uid=1000,gid=1000 {share_name} {guest_dst}"
        remote_exec(cmd, machine_id)
        log.info(f"Mountpoint {host_src} -> {guest_dst} created")
    else:
        log.info(f"Mountpoint {host_src} -> {guest_dst} already exists")

    record_mountpoint(host_src, guest_dst, machine_name)


def mount_all_recorded_mountpoints():
    """ mounts all mountpoints recorded in mountpoint config. """
    # TODO get machine name from mountpoint config to support multiple vms
    machine_name = "asmr.dev"

    if mountpoint_file.exists():
        with open(mountpoint_file, 'r') as fd:
            for mountpoint in [l.strip() for l in fd.readlines()]:
                if mountpoint != '':
                    host_src, guest_dst = mountpoint.split(':')
                    mount(pathlib.Path(host_src),
                          pathlib.Path(guest_dst),
                          machine_name)


# TODO *update all these functions to take an optional machine_name
# as a paramter and then lookup the machine_id with the above
# memoized function.
def suspend(machine_id: str):
    log.info(f"suspending {machine_id}...")
    asmr.process.run(f"vagrant suspend {machine_id}")


# TODO *update
def halt(machine_id: str):
    log.info(f"halting {machine_id}...")
    asmr.process.run(f"vagrant halt {machine_id}")


# TODO *update
def destroy(machine_id: str):
    log.info(f"destroying {machine_id}...")
    asmr.process.run(f"vagrant destroy --force {machine_id}")


# TODO *update
def up(machine_id: str=None):
    if machine_id:
        log.info(f"starting up {machine_id}...")
        log.info(f"This may take a minute or two...be patient...")
        asmr.process.run(f"vagrant up {machine_id}")
    else:
        # we must be within the project_root/.dev-environ here.
        log.info(f"Creating ASMR Dev Environment...")
        log.info(f"This will take several minutes...please be patient...")
        asmr.process.run(f"vagrant up", capture=False)


# TODO *update
def resume(machine_id: str):
    log.info(f"resuming {machine_id}...")
    asmr.process.run(f"vagrant resume {machine_id}")


# TODO *update
def remote_exec(cmd: str, machine_id: str):
    """execute a command remotely on the virtual machine. """
    asmr.process.run(f"vagrant ssh -c \"{cmd}\" {machine_id}",
                     logger=None)


# TODO *update
def ssh(machine_id: str, dest: pathlib.Path = "/asmr/projects"):
    # Thanks sholsapp! see https://www.py4u.net/discuss/224642
    subprocess.call(f"vagrant ssh -c \"cd {dest}; cat /.ASMR_DEV_ENV; bash --login\" {machine_id}",
                    shell=True)


def reload():
    # reload vagrantfile
    pass


def provision():
    """ provision the dev vm.

    We must be within a dev-environment directory with a Vagrantfile
    for this to work.
    """
    asmr.process.run(f"vagrant provision", capture=False)
