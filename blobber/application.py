#!/usr/bin/env python
import tempfile
import os
import hashlib
import logging
import time

import utils
from functools import partial
from bottle import Bottle, request, abort, response
from amazons3_backend import upload_to_AmazonS3
from config import METADATA_SIZE_LIMIT, FILE_SIZE_LIMIT

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


def set_aws_request_headers(filename, default_mimetype):
    mimetype = utils.get_blob_mimetype(filename, default_mimetype)

    headers = {
        'Content-Type': mimetype,
    }

    if mimetype == default_mimetype:
        headers['Content-Disposition'] = 'attachment; filename=\"%s\"' % (filename)
    else:
        headers['Content-Disposition'] = 'inline; filename=\"%s\"' % (filename)

    return headers


@app.post('/blobs/:hashalgo/:blobhash')
def upload_blob(hashalgo, blobhash):
    data = request.files.data
    if not data.file:
        print 'File upload missed.'
        abort(400, "Missing uploaded file")

    tmpfile, _hsh = save_request_file(data.file, hashalgo)
    try:
        if _hsh != blobhash:
            print 'Invalid hash for the file attached.'
            abort(400, "Invalid hash")
        # Prepare metadata along with the actual data file
        # Some is server-side determined, some is taken from request
        meta_dict = {
            'upload_time': int(time.time()),
            'upload_ip': request.remote_addr,
            'filesize': os.path.getsize(tmpfile),
        }

        if meta_dict['filesize'] > FILE_SIZE_LIMIT:
            print 'File size exceeds size limit.'
            abort(400, 'File size limit exceeded!')

        fields = ('filename', 'branch', 'mimetype')
        for field in fields:
            if field not in request.forms:
                print 'Missing %s ' % field
                abort(400, '%s missing' % field)

        filename = utils.slice_filename(request.forms['filename'])
        if not utils.filetype_allowed(filename):
            print 'File type not allowed on server'
            abort(400, 'File type not allowed  to be uploaded')

        # make sure to drop other possible metadata fields
        meta_dict.update({k: request.forms[k] for k in fields})
        # make sure metadata total size does not exceed limit
        meta_size = sum([len(str(k)) + len(str(v))
                         for k,v in meta_dict.items()])
        if meta_size > METADATA_SIZE_LIMIT:
            print 'Metadata limit exceeded'
            abort(400, 'Metadata exceeds limits')

        # add/update file on S3 machine along with its metadata
        headers = set_aws_request_headers(filename, meta_dict['mimetype'])
        # update metadata should it contain a renderable mimetype
        meta_dict['mimetype'] = headers['Content-Type']

        upload_to_AmazonS3(hashalgo,
                           blobhash,
                           tmpfile,
                           headers,
                           meta_dict)

        response.status = 202
    finally:
        print tmpfile
        os.unlink(tmpfile)


def main():
    app.run(host='0.0.0.0', port=8080, debug=True, reloader=True)

if __name__ == '__main__':
    main()
