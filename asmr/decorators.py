""" Decorators. """

import datetime
import functools


def interval(ms: int):
    """ Only execute the decorated function is 'ms' time has passed. """
    def _decorator(fn):
        start = datetime.datetime.now()
        @functools.wraps(fn)
        def _wrapper(*args, **kwargs):
            nonlocal start
            now = datetime.datetime.now()
            if (now - start).total_seconds() * 1000 >= ms:
                start = datetime.datetime.now()
                fn(*args, **kwargs)
        return _wrapper
    return _decorator


# Thanks Claudiu, John Kugelman
# see https://stackoverflow.com/a/279586
def static_variables(**kwargs):
    """ add static variables to functions. """
    def _decorator(fn):
        for k in kwargs:
            setattr(fn, k, kwargs[k])
        return fn
    return _decorator
