""" Logging utilities. """

import atexit
import contextlib
import datetime
import enum
import functools
import io
import os
import pathlib
import shutil
import sys
import typing as t

import asmr.env
import asmr.string
from asmr.decorators import interval
from asmr.ansi import color, style, escape_ansi


_default_logs_dir = os.getenv(asmr.env.logs) or '.logs'


class Level(enum.Enum):
    debug   = 0
    info    = 1
    warning = 2
    error   = 3


class StreamDemux(io.StringIO):
    """ Demultiplex output to stream and file. """
    def __init__(self, stream: io.StringIO, log: t.TextIO):
        self.stream = stream
        self.log    = log

    def write(self, data):
        self.stream.write(data)
        self.log.write(escape_ansi(data))

    def flush(self):
        self.stream.flush()


def _default_fmt_fn(name: str, level: Level, msg: str) -> str:
    time_fmt = color.cyan_light(datetime.datetime.now().isoformat())
    level_fmt = {
        Level.debug:   color.white("[debug]"),
        Level.info:    color.green_light("[info]"),
        Level.warning: color.yellow_light("[warning]"),
        Level.error:   color.red_light("[error]"),
    }
    name_fmt = color.magenta_light(f"({name})")
    msg_fmt  = {
        Level.debug:   color.white(msg),
        Level.info:    color.green_light(msg),
        Level.warning: color.yellow_light(msg),
        Level.error:   color.red_light(msg),
    }

    return f"{time_fmt} {level_fmt[level]} {name_fmt} {msg_fmt[level]}"


def clear_line():
    sys.stdout.write("\r")
    sys.stdout.write(' ' * shutil.get_terminal_size().columns)
    sys.stdout.write("\r")


class Formatter:
    def __init__(self, fmt_fn=_default_fmt_fn):
        self.fmt_fn = fmt_fn

    def __call__(self, name: str, level: Level, msg: str) -> str:
        return self.fmt_fn(name, level, msg)


class Logger:
    def __init__(self,
                 name: str,
                 dirpath: pathlib.Path,
                 to_file=True,
                 fmt=Formatter()):

        self.name = name

        if to_file:
            self.log = (dirpath/name).with_suffix(".log").open(mode="a")
            self.err = (dirpath/name).with_suffix(".err").open(mode="a")

            self.stdout = StreamDemux(sys.stdout, self.log)
            self.stderr = StreamDemux(sys.stderr, self.err)
        else:
            self.log = None
            self.err = None

            self.stdout = sys.stdout
            self.stderr = sys.stderr

        self.level = Level.info
        self.fmt   = fmt

    def set_level(self, level: Level):
        self.level = level

    def set_format(self, fmt: Formatter):
        self.fmt = fmt

    def filter_and_format(level):
        """ Decorator to filter and format log messages of various levels."""
        def _decorator(fn):
            @functools.wraps(fn)
            def _wrapper(*args):
                current_level = args[0].level
                fmt_fn        = args[0].fmt
                name          = args[0].name
                message       = args[1]
                if level.value >= current_level.value:
                    fn(args[0], fmt_fn(name, level, message))
            return _wrapper
        return _decorator

    @contextlib.contextmanager
    def progress(self, prefix: str, end_suffix=None, update_ms=100):
        """ Logs the progress of an incremental task.

        Usage Example:
            with my_log.progress("doing some task") as progress:
                for x in range(100):
                    progress(x/100, suffix="% complete")

        Note: the yielded 'progress' function accepts a float between [0, 1]
        as its first argument.
        """

        _percent = 0
        _seq     = asmr.string.sequence("◯", "◴◷◶◵")
        @interval(update_ms)
        def updater_fn(percent: float, suffix=""):
            nonlocal _seq, _percent
            columns    = shutil.get_terminal_size().columns
            _percent   = percent * 100
            width      = columns - (len(suffix) + 2)

            bar_seq         = _seq[:(int(percent * width))]
            bar_done        = f"{style.bold(color.green_light(bar_seq[:-1]))}"
            bar_in_progress = f"{style.bold(color.cyan_light(bar_seq[-1]))}"
            bar_remaining   = ' '*(width - len(bar_seq))

            delim_l_fmt  = f"{color.white('[')}"
            delim_r_fmt  = f"{color.white(']')}"
            bar_fmt    = f"{bar_done}{bar_in_progress}{bar_remaining}"
            suffix_fmt = f"{color.green_light(suffix)}"

            clear_line()
            sys.stdout.write("\r")
            sys.stdout.write(f"{delim_l_fmt}{bar_fmt}{delim_r_fmt}{suffix_fmt}")
            sys.stdout.flush()

        try:
            self.info(f"{prefix} [in progress]")
            yield updater_fn
        except Exception as e:
            clear_line()
            self.error(f"{e} -- {prefix} [aborted {_percent:1.1f}%]")
            raise e
        except KeyboardInterrupt:
            clear_line()
            self.warning(f"stopped (ctrl-c)! {prefix} [aborted {_percent:1.1f}%]")
            sys.exit()

        # Thanks Alex Volkov! see https://stackoverflow.com/a/33024739
        updater_fn.__wrapped__(1, end_suffix or "")
        self.info(f"{prefix} [done]")


    @filter_and_format(Level.debug)
    def debug(self, msg: str):
        self.stdout.write(f"{msg}\n")

    @filter_and_format(Level.info)
    def info(self, msg: str):
        self.stdout.write(f"{msg}\n")

    @filter_and_format(Level.warning)
    def warning(self, msg: str):
        self.stdout.write(f"{msg}\n")

    @filter_and_format(Level.error)
    def error(self, msg: str):
        self.stderr.write(f"{msg}\n")

    def close(self):
        if self.log:
            self.log.flush()
            self.log.close()
        if self.err:
            self.err.flush()
            self.err.close()


class LogCtl:
    def __init__(self, log_dir: pathlib.Path, fmt=Formatter()):
        self.log_dir       = log_dir
        self.loggers       = {}
        self.fmt           = fmt

        ## ensure log_dir exists.
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def get_logger(self, name: str, to_file=True) -> Logger:
        if name not in self.loggers:
            self.loggers[name] = Logger(name,
                                        self.log_dir,
                                        to_file=to_file,
                                        fmt=self.fmt)
        return self.loggers[name]

    def set_level(self, level: Level):
        for logger in self.loggers.values():
            logger.set_level(level)

    def set_level(self, fmt: Formatter):
        self.fmt = fmt
        for logger in self.loggers.values():
            logger.set_format(fmt)

    def close(self):
        for logger in self.loggers.values():
            logger.close()


_logctl = LogCtl(pathlib.Path(_default_logs_dir))


def get_logger(name="asmr", to_file=True) -> Logger:
    return _logctl.get_logger(name, to_file=to_file)

def set_level(level: Level):
    _logctl.set_level(level)

def set_format(fmt: Formatter):
    _logctl.set_format(fmt)

def close():
    _logctl.close()


# on exit, always close logs.
atexit.register(close)
