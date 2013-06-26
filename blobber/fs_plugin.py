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


class ManifestBackend(object):
    def __init__(self, config):
        self.config = config
        self.dir = config['dir']

    def _make_path(self, hsh):
        return os.path.join(self.dir, hsh[0:2], hsh[2:4], hsh)

    def has_archive_manifest(self, hsh):
        return os.path.exists(self._make_path(hsh))

    def get_manifestid_by_archive_hash(self, hsh):
        return open(self._make_path(hsh), 'rb').read()

    def add_manifest(self, m, archive_hash=None):
        manifest_id = uuid.uuid4().hex
        # Save the manifests
        with mkdiropen(self._make_path(manifest_id), 'wb') as f:
            f.write(manifest.to_json(m))
        if archive_hash:
            with mkdiropen(self._make_path(archive_hash), 'wb') as f:
                f.write(manifest_id)
        return manifest_id
