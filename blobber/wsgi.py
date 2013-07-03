#!/usr/bin/env python
import tempfile
import os
import hashlib
import json

from datetime import datetime
from functools import partial

from bottle import Bottle, request, abort, response, static_file
from blobber.sqlite_plugin import MetadataBackend
from blobber.backend import BlobberBackend

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
        print 'miss uploaded file'
        abort(400, "Missing uploaded file")

    tmpfile, _hsh = save_request_file(data.file, hashalgo)
    try:
        if _hsh != blobhash:
            print 'invalid hash'
            abort(400, "Invalid hash")

        app.backend.add_blob(hashalgo, blobhash, tmpfile)
        # determine some of the metadata
        meta_dict = {
            'blobhash': blobhash,
            'upload_time': datetime.now(),
            'upload_ip': request.remote_addr
        }

        # the rest of the metadata is taken from request
        fields = ('filename', 'filesize', 'branch', 'mimetype')
        for field in fields:
            if field not in request.forms:
                print '%s missing' % field
                abort(400, '%s missing' % field)

        meta_dict.update(request.forms)
        app.meta_backend.add_blob_metadata(**meta_dict)

        response.status = 202
    finally:
        print tmpfile
        os.unlink(tmpfile)


@app.get('/blobs/:hashalgo/:blobhash')
def get_blob(hashalgo, blobhash):
    path = app.backend.get_blob_path(hashalgo, blobhash)
    return static_file(*reversed(os.path.split(path)), mimetype='application/octet-stream')


def main():
    from blobber.fs_plugin import FileBackend
    B = BlobberBackend({})
    B.files = FileBackend({"dir": "file_store"})
    app.backend = B

    metaB = MetadataBackend({'name': 'mydatabase.db'})
    app.meta_backend = metaB

    app.run(host='127.0.0.1', port=8080, debug=True, reloader=True)

if __name__ == '__main__':
    main()
