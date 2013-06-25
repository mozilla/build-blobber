#!/usr/bin/env python
import tempfile
import os
import hashlib
import json

from functools import partial

from bottle import Bottle, request, abort, response, static_file

from blobber.backend import BlobberBackend, MissingBlobsError

import logging
log = logging.getLogger(__name__)

app = Bottle()


def save_request_file(fileobj, hashalgo=None):
    """
    Saves uploaded file `fileobj` and returns its filename
    """
    fd, tmpfile = tempfile.mkstemp()
    h = None
    if hashalgo:
        h = hashlib.new(hashalgo)

    try:
        nread = 0
        for block in iter(partial(fileobj.read, 1024 ** 2), ''):
            nread += len(block)
            if h:
                h.update(block)
            os.write(fd, block)
        os.close(fd)
        return tmpfile, h.hexdigest()
    except:
        os.close(fd)
        os.unlink(tmpfile)
        raise


@app.post('/blobs/:hashalgo/:blobhash')
def upload_blob(hashalgo, blobhash):
    if app.backend.has_blob(hashalgo, blobhash):
        # All done!
        response.status = 202
        # consume the file to be nice
        data = request.files.data
        return

    data = request.files.data
    if not data.file:
        abort(400, "Missing uploaded file")

    tmpfile, _hsh = save_request_file(data.file, hashalgo)
    try:
        if _hsh != blobhash:
            abort(400, "Invalid hash")

        app.backend.add_blob(hashalgo, blobhash, tmpfile)
        response.status = 202
    finally:
        print tmpfile
        #os.unlink(tmpfile)


@app.get('/blobs/:hashalgo/:blobhash')
def get_blob(hashalgo, blobhash):
    path = app.backend.get_blob_path(hashalgo, blobhash)
    return static_file(*reversed(os.path.split(path)), mimetype='application/octet-stream')


@app.post('/manifests')
def upload_manifest():
    # If the posted data is too large, we can't process it in memory and need
    # to spawn a worker
    manifest = request.json
    if manifest is None:
        # XXX TODO: do this in a separate process otherwise we can use too much
        # ram
        manifest = json.load(request.body)

    try:
        manifest_id = app.backend.import_manifest(manifest)
        response.status = 202
        return {'manifest_id': manifest_id}
    except MissingBlobsError as e:
        response.status = 400
        return {"missing_blobs": e.missing_blobs}


@app.post("/archives")
def upload_archive():
    # Save archive to temporary location
    data = request.files.data
    if not data.file:
        abort(400)

    tmpfile, _hsh = save_request_file(data.file)

    try:
        manifest_id = app.backend.injest_archive(tmpfile)
        # Return manifest id
        return str(manifest_id)
    finally:
        os.unlink(tmpfile)


def main():
    from blobber.fs_plugin import FileBackend, ManifestBackend
    B = BlobberBackend({})
    B.db = ManifestBackend({"dir": "manifests"})
    B.files = FileBackend({"dir": "file_store"})

    app.backend = B
    app.run(host='0.0.0.0', port=8080, debug=True, reloader=True)

if __name__ == '__main__':
    main()
