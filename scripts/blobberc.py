#!/usr/bin/env python
"""Usage: blobberc.py -u URL... [-a] [-v] FILE...

-u, --url URL          URL to blobber server to upload to. Multiple URLs can be
                       specified, and they will be tried in random order
-a, --unpack-archives  Unpack archives (e.g. .zip, .tar.gz) before uploading
-v, --verbose          Increase verbosity

FILE                   Local file(s) to upload
"""
import random
import urlparse
import os
import shutil
import urllib2

import requests
import requests.exceptions
import poster.encode

import blobber.manifest
import blobber.archives
import blobber.hashes

import logging
log = logging.getLogger(__name__)


def has_blob(urls, hashalgo, blobhash):
    url = urlparse.urljoin(urls[0], '/blobs/{}/{}'.format(hashalgo, blobhash))
    response = requests.head(url)
    return response.ok


def upload_file(urls, filename, hashalgo='sha1', blobhash=None, check_first=False):
    if blobhash is None:
        blobhash = blobber.hashes.filehash(filename, hashalgo)

    if check_first and has_blob(urls, hashalgo, blobhash):
        return blobhash

    url = urlparse.urljoin(urls[0], '/blobs/{}/{}'.format(hashalgo, blobhash))

    log.debug("posting file to %s", url)

    datagen, headers = poster.encode.multipart_encode({
        'data': open(filename, 'rb'),
        'filename': filename,
        'filesize': os.path.getsize(filename),
        'branch': 'branch-input',
        'mimetype': 'application/octet-stream',
    })
    req = urllib2.Request(url, datagen, headers)
    urllib2.urlopen(req)



def main():
    from docopt import docopt
    import poster.streaminghttp
    poster.streaminghttp.register_openers()

    args = docopt(__doc__)

    if args['--verbose']:
        loglevel = logging.DEBUG
    else:
        loglevel = logging.INFO

    logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=loglevel)
    logging.getLogger('requests').setLevel(logging.WARN)


    for f in args['FILE']:
        if os.path.isfile(f):
            blob_id = upload_file(args['--url'], f, check_first=False)
            print f, blob_id

if __name__ == '__main__':
    main()
