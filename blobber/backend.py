import os

from blobber.hashes import sha1sum
from blobber.archives import unpack_archive
from blobber.manifest import make_manifest, FILE, convert_manifest


class MissingBlobsError(Exception):
    def __init__(self, missing_blobs):
        self.missing_blobs = missing_blobs


class BlobberBackend(object):
    def __init__(self, config):
        self.config = config
        self.db = None
        self.files = None

    def has_blob(self, hashalgo, blobhash):
        return self.files.has_blob(hashalgo, blobhash)

    def add_blob(self, hashalgo, blobhash, tmpfile):
        return self.files.add_blob(hashalgo, blobhash, tmpfile)

    def open_blob(self, hashalgo, blobhash):
        return self.files.open_blob(hashalgo, blobhash)

    def get_blob_path(self, hashalgo, blobhash):
        return self.files.get_blob_path(hashalgo, blobhash)

    def delete_blob(self, hashalgo, blobhash):
        return self.files.delete_blob(hashalgo, blobhash)

if __name__ == '__main__':
    from blobber.fs_plugin import FileBackend
    B = BlobberBackend({})
    B.files = FileBackend({"dir": "file_store"})

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+")

    args = parser.parse_args()
    for f in args.files:
        _, added = B.injest_archive(f)
        print f, added
