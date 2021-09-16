""" ANSI styles. """

import typing as t
from enum import Enum
import re


class _ansi_color(Enum):
    black   = 30
    red     = 31
    green   = 32
    yellow  = 33
    blue    = 34
    magenta = 35
    cyan    = 36
    white   = 37
    reset   = 0


def _reset() -> str:
    return u"\u001b["+str(_ansi_color.reset.value)+u"m"

def _foreground(color: _ansi_color, s: t.Any, light=False) -> str:
    return u"\u001b["+str(color.value)+f"{';1' if light else ''}m"+str(s)+_reset()

def _background(color: _ansi_color, s: t.Any, light=False) -> str:
    return u"\u001b["+str(color.value+10)+f"{';1' if light else ''}m"+str(s)+_reset()

def _bold(s: t.Any):
    return u"\u001b[1m"+str(s)+_reset()

def _underline(s: t.Any):
    return u"\u001b[4m"+str(s)+_reset()

class style(Enum):
    bold      = lambda t : _bold(t)
    underline = lambda t : _underline(t)

class color(Enum):
    black   = lambda t : _foreground(_ansi_color.black, t)
    red     = lambda t : _foreground(_ansi_color.red, t)
    green   = lambda t : _foreground(_ansi_color.green, t)
    yellow  = lambda t : _foreground(_ansi_color.yellow, t)
    blue    = lambda t : _foreground(_ansi_color.blue, t)
    magenta = lambda t : _foreground(_ansi_color.magenta, t)
    cyan    = lambda t : _foreground(_ansi_color.cyan, t)
    white   = lambda t : _foreground(_ansi_color.white, t)

    black_light   = lambda t : _foreground(_ansi_color.black, t, light=True)
    red_light     = lambda t : _foreground(_ansi_color.red, t, light=True)
    green_light   = lambda t : _foreground(_ansi_color.green, t, light=True)
    yellow_light  = lambda t : _foreground(_ansi_color.yellow, t, light=True)
    blue_light    = lambda t : _foreground(_ansi_color.blue, t, light=True)
    magenta_light = lambda t : _foreground(_ansi_color.magenta, t, light=True)
    cyan_light    = lambda t : _foreground(_ansi_color.cyan, t, light=True)
    white_light   = lambda t : _foreground(_ansi_color.white, t, light=True)

    black_bg   = lambda t : _background(_ansi_color.black, t)
    red_bg     = lambda t : _background(_ansi_color.red, t)
    green_bg   = lambda t : _background(_ansi_color.green, t)
    yellow_bg  = lambda t : _background(_ansi_color.yellow, t)
    blue_bg    = lambda t : _background(_ansi_color.blue, t)
    magenta_bg = lambda t : _background(_ansi_color.magenta, t)
    cyan_bg    = lambda t : _background(_ansi_color.cyan, t)
    white_bg   = lambda t : _background(_ansi_color.white, t)

    black_light_bg   = lambda t : _background(_ansi_color.black, t, light=True)
    red_light_bg     = lambda t : _background(_ansi_color.red, t, light=True)
    green_light_bg   = lambda t : _background(_ansi_color.green, t, light=True)
    yellow_light_bg  = lambda t : _background(_ansi_color.yellow, t, light=True)
    blue_light_bg    = lambda t : _background(_ansi_color.blue, t, light=True)
    magenta_light_bg = lambda t : _background(_ansi_color.magenta, t, light=True)
    cyan_light_bg    = lambda t : _background(_ansi_color.cyan, t, light=True)
    white_light_bg   = lambda t : _background(_ansi_color.white, t, light=True)


# thanks @Manogna!
# https://www.tutorialspoint.com/How-can-I-remove-the-ANSI-escape-sequences-from-a-string-in-python
_ansi_escape =re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')
def escape_ansi(line: str) -> str:
    return _ansi_escape.sub('', line)
