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

    def injest_archive(self, filename):
        """
        Returns a manifest id
        """
        filename = os.path.abspath(filename)

        # Hash archive
        hsh = sha1sum(filename)
        # Check if we're already done this work
        if self.db.has_archive_manifest(hsh):
            return self.db.get_manifestid_by_archive_hash(hsh), 0

        # Unpack it
        tmpdir = unpack_archive(filename)

        # Generate manifest for contents
        manifest = make_manifest(tmpdir)

        # Import files
        added = self.import_files(tmpdir)

        # Return manifest id
        manifest_id = self.db.add_manifest(manifest, archive_hash=hsh)
        return manifest_id, added

    def import_files(self, hashalgo, dirname):
        added = 0
        for root, dirs, files in os.walk(dirname):
            for f in files:
                f = os.path.join(root, f)
                if not self.files.has_file(f):
                    self.files.import_file(hashalgo, f)
                    added += 1
        return added

    def import_manifest(self, manifest):
        # Check if we have all the file objects
        convert_manifest(manifest)
        missing_blobs = []
        for e in (e for e in manifest['entries'] if e.type == FILE):
            if not self.files.has_blob(e.hashalgo, e.hash):
                missing_blobs.append((e.hashalgo, e.hash))

        if missing_blobs:
            raise MissingBlobsError(missing_blobs)

        manifest_id = self.db.add_manifest(manifest)
        return manifest_id

    def has_blob(self, hashalgo, blobhash):
        return self.files.has_blob(hashalgo, blobhash)

    def add_blob(self, hashalgo, blobhash, tmpfile):
        return self.files.add_blob(hashalgo, blobhash, tmpfile)

    def open_blob(self, hashalgo, blobhash):
        return self.files.open_blob(hashalgo, blobhash)

    def get_blob_path(self, hashalgo, blobhash):
        return self.files.get_blob_path(hashalgo, blobhash)


if __name__ == '__main__':
    from blobber.fs_plugin import FileBackend, ManifestBackend
    B = BlobberBackend({})
    B.db = ManifestBackend({"dir": "manifests"})
    B.files = FileBackend({"dir": "file_store"})

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+")

    args = parser.parse_args()
    for f in args.files:
        _, added = B.injest_archive(f)
        print f, added
