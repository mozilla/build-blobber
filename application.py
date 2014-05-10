#!/usr/bin/env python

import tempfile
import os
import hashlib
import logging
import time
from functools import partial
from bottle import Bottle, request, response, HTTPError
try:
    import simplejson as json
except ImportError:
    import json

from blobber import get_blob_mimetype, filetype_allowed, security_config
from blobber.decorators import login_required, check_client_ip, attach_required
from blobber.amazons3_backend import upload_to_AmazonS3
from blobber.config import METADATA_SIZE_LIMIT, FILE_SIZE_LIMIT

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
        for block in iter(partial(fileobj.read, 1024 ** 2), ''):
            if h:
                h.update(block)
            os.write(fd, block)
        os.close(fd)
        return tmpfile, h.hexdigest()
    except:
        os.close(fd)
        os.unlink(tmpfile)
        raise


def set_aws_request_headers(filename, default_mimetype, compression):
    """
    Set headers for file to Amazon S3 storage use and return them

    """
    mimetype = get_blob_mimetype(filename, default_mimetype)
    headers = {
        'Content-Type': mimetype,
        'Content-Disposition': 'inline; filename="%s"' % (filename),
    }
    if compression:
        headers['Content-Encoding'] = compression

    return headers


@app.get('/blobs/whitelist')
def get_allowed_filetypes():
    response.content_type = 'application/json'
    ret = {
        "whitelist": security_config.get('allowed_filetypes', [])
    }
    return json.dumps(ret)


@app.post('/blobs/:hashalgo/:blobhash')
@check_client_ip
@login_required
@attach_required
def upload_blob(hashalgo, blobhash):
    """
    Receives the file from client. Save a local temporary copy of the file to
    make sure the hash is correct. Determines the metadata about the file and
    further uploads it to Amazon S3 storage.
    Returns #202 response on success, or different error code with accordingly
    error message should any of them occur
    """
    tmpfile, _hsh = save_request_file(request.files.blob.file, hashalgo)
    try:
        if _hsh != blobhash:
            raise HTTPError(status=403,
                            x_blobber_msg='Invalid hash!')
        # Prepare metadata along with the actual data file
        # Some is server-side determined, some is taken from request
        meta_dict = {
            'upload_time': int(time.time()),
            'upload_ip': request.remote_addr,
            'filesize': os.path.getsize(tmpfile),
            'filename': request.files.blob.filename,
        }

        if meta_dict['filesize'] > FILE_SIZE_LIMIT:
            raise HTTPError(status=403,
                            x_blobber_msg='File size exceeds size limit!')

        fields = ('branch',)
        for field in fields:
            if field not in request.forms:
                raise HTTPError(
                    status=403,
                    x_blobber_msg='Metadata %s field missing!' % field)

        filename = request.files.blob.filename
        if not filetype_allowed(filename):
            raise HTTPError(status=403,
                            x_blobber_msg='File type not allowed on server!')

        # make sure to drop other possible metadata fields
        meta_dict.update({k: request.forms[k] for k in fields})

        compression = 'gzip' if request.forms.get('compressed', None) == 'True' else None
        headers = set_aws_request_headers(filename, request.files.blob.type,
                                          compression)
        # update metadata should it contain a renderable mimetype
        meta_dict['mimetype'] = headers['Content-Type']

        # make sure metadata total size does not exceed limit
        meta_size = sum([len(str(k)) + len(str(v))
                         for k, v in meta_dict.items()])
        if meta_size > METADATA_SIZE_LIMIT:
            raise HTTPError(status=403,
                            x_blobber_msg='Metadata limit exceeded!')

        # add/update file on S3 machine along with its metadata
        try:
            blob_url = upload_to_AmazonS3(hashalgo, blobhash, tmpfile, headers,
                                          meta_dict)
            # return URL in reponse headers
            response.set_header('x-blob-url', blob_url)
            response.set_header('x-blob-filename', filename)
            response.status = 202
        except Exception:
            log.error("Failed uploading to S3", exc_info=True)
            raise HTTPError(status=500, x_blobber_msg="Failed uploading to S3")

    finally:
        os.unlink(tmpfile)


application = app


def main():
    app.run(host='0.0.0.0', port=8080, debug=False, reloader=True)


if __name__ == '__main__':
    logging.basicConfig()
    main()
