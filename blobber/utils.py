import os
import sys

from contextlib import contextmanager

from config import blob_mimetypes

WINDOWS = (sys.platform.startswith("win") or
          sys.platform.startswith("cygwin"))


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


def get_blob_mimetype(filename, guessed_mimetype):
    extension = filename.split('.')[-1]
    mimetype = blob_mimetypes.get(extension, None)
    if not mimetype:
        return guessed_mimetype
    return mimetype


def slice_filename(string):
    if WINDOWS:
        return string.split('\\')[-1]
    else:
        return string.split('/')[-1]
