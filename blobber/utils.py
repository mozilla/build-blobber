import os
from contextlib import contextmanager


@contextmanager
def ignored(*exceptions):
    try:
        yield
    except exceptions:
        pass


def mkdiropen(filename, mode):
    d = os.path.dirname(filename)
    if not os.path.exists(d):
        with ignored(OSError):
            os.makedirs(d)

    return open(filename, mode)
