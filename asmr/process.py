""" Process utilities. """

import collections
import shlex
import subprocess
import typing as t

import asmr.logging

log = asmr.logging.get_logger()


Result = collections.namedtuple('Result', ['retcode','stdout','stderr'])

class Pipeline:
    """ A process pipeline.

    Example:
        proc = asmr.process.Pipeline("cat /etc/hosts")
        proc|= "grep 127.0.0.1"
        proc|= ["awk", "{print $1}"]

        # get results
        ret, stdout, stderr = proc()
    """
    def __init__(self,
                 cmd: t.Union[t.List, str],
                 stderr_to_stdout=False,
                 logger=log,
                 capture=True):
        self.capture = capture
        self.pipeline = []
        self.logger = logger
        self.stderr_to_stdout = stderr_to_stdout

        self._pipe(cmd)

    def __or__(self, rhs: t.Union[t.List, str]):
        """ simulate '|' in Bash. """
        if not self.capture:
            return self

        # Thanks xtofl!
        # see https://dev.to/xtofl/i-want-my-bash-pipe-34i2
        self._pipe(rhs, self.pipeline[-1].stdout)
        return self

    def __call__(self) -> Result:
        """ gets final results & output. """
        normalize = lambda s : list(filter(None, s.decode('utf-8').split('\n')))

        tail_proc = self.pipeline[-1]
        tail_proc.communicate()

        # initialize results
        stderr  = []
        stdout  = []
        retcode = tail_proc.returncode

        if not self.capture:
            return Result(retcode, stdout, stderr)

        # only include stdout/err from tail on success.
        procs = [tail_proc] if retcode == 0 else self.pipeline

        # unwind process stack
        for proc in procs:
            r_stdout, r_stderr = proc.communicate()
            _stderr = normalize(r_stderr)
            _stdout = normalize(r_stdout)

            # consolidate stderr & stdout?
            if self.stderr_to_stdout:
                _stdout = _stderr + _stdout
                _stderr = []

            stderr+= _stderr
            stdout+= _stdout

        # log output
        if self.logger:
            for err in stderr:
                self.logger.error(err)
            for out in stdout:
                self.logger.info(out)

        return Result(retcode, stdout, stderr)

    def _pipe(self, cmd: t.Union[t.List, str], stdin=None):
        if isinstance(cmd, str):
            cmd = shlex.split(cmd)

        stdout = subprocess.PIPE
        stderr = subprocess.PIPE

        if not self.capture:
            stdout = None
            stderr = None

        # Thanks Doug Hellmann!
        # see https://pymotw.com/2/subprocess/#connecting-segments-of-a-pipe
        proc = subprocess.Popen(cmd,
                                stdin=stdin,
                                stdout=stdout,
                                stderr=stderr)
        self.pipeline.append(proc)


def pipeline(cmds: t.List[t.Union[t.List, str]],
             stderr_to_stdout=False,
             logger=log) -> Result:
    """ execute a subprocess pipeline.

    This function is similar to run, however it suports piping commands
    similar to piping in a Bash shell, e.g. cat 'passwds | grep secret'.
    Alternatively, one could directly use the Pipeline class.

    Example:
        retcode, stdout, stderr = asmr.process.pipeline([
            "cat /etc/hosts",
            "grep 127.0.0.1",
            ["awk", "{print $1}"],
        ], logger=None)
    """
    pipeline = Pipeline(cmds[0], stderr_to_stdout=stderr_to_stdout, logger=logger)
    for cmd in cmds[1:]:
        pipeline|=cmd
    return pipeline()


def run(cmd: t.Union[t.List[str], str],
        stderr_to_stdout=False,
        logger=log,
        capture=True) -> Result:
    return Pipeline(cmd,
                    stderr_to_stdout=stderr_to_stdout,
                    logger=logger,
                    capture=capture)()
