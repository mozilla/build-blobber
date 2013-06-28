import os
import uuid
from functools import partial

import blobber.manifest as manifest
from blobber.utils import mkdiropen


class FileBackend(object):
    def __init__(self, config):
        self.config = config
        self.dir = config['dir']

    def _make_path(self, hashalgo, blobhash):
        d = os.path.join(self.dir, hashalgo, blobhash[0:2], blobhash[2:4])
        p = os.path.join(d, blobhash)
        return p

    def has_blob(self, hashalgo, blobhash):
        return os.path.exists(self._make_path(hashalgo, blobhash))

    def open_blob(self, hashalgo, blobhash):
        return open(self._make_path(hashalgo, blobhash))

    def get_blob_path(self, hashalgo, blobhash):
        return self._make_path(hashalgo, blobhash)

    def blob_size(self, hashalgo, blobhash):
        return os.path.getsize(self._make_path(hashalgo, blobhash))

    def add_blob(self, hashalgo, blobhash, filename):
        p = self._make_path(hashalgo, blobhash)
        if os.path.exists(p):
            return

        with mkdiropen(p + ".tmp", "wb") as dst, open(filename, 'rb') as src:
            for block in iter(partial(src.read, 1024 ** 2), ''):
                dst.write(block)
        os.rename(p + ".tmp", p)
