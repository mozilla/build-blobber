import redis
import uuid

import blobber.manifest as manifest


class ManifestBackend(object):
    def __init__(self, config):
        self.config = config
        self.conn = redis.StrictRedis()

    def has_archive_manifest(self, hsh):
        return self.conn.hexists("archive_manifests", hsh)

    def get_manifestid_by_archive_hash(self, hsh):
        return self.conn.hget("archive_manifests", hsh)

    def add_manifest(self, m, archive_hash=None):
        manifest_id = uuid.uuid4()
        self.conn.hset("manifests", manifest_id, manifest.to_json(m))
        if archive_hash:
            self.conn.hset("archive_manifests", archive_hash, manifest_id)
        return manifest_id
