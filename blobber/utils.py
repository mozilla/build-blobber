import os
import sys

from contextlib import contextmanager

from config import blob_mimetypes


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


# TODO: TO-REVIEW
def get_blob_mimetype(filename, default_mimetype):
    extension = filename.split('.')[-1].lower()
    mimetype = blob_mimetypes.get(extension, default_mimetype)
    return mimetype


# TODO: TO-REVIEW
def slice_filename(filename_path):
    # filename_path can be any platform-based (OSX, Win, Linux)
    filename_path = os.path.normpath(filename_path)
    return filename_path.split('\\')[-1].split('/')[-1]
