#!/usr/bin/env python
"""Usage: blobberc.py -u URL... [-b BRANCH] [-v] FILE...

-u, --url URL          URL to blobber server to upload to. Multiple URLs can be
                       specified, and they will be tried in random order
-b, --branch BRANCH    Specify branch for the file (e.g. try, mozilla-central)
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

import blobber.hashes

import logging
log = logging.getLogger(__name__)


def upload_file(urls, filename, hashalgo='sha1', blobhash=None,
                branch='mozilla-inbound'):
    if blobhash is None:
        blobhash = blobber.hashes.filehash(filename, hashalgo)

    url = urlparse.urljoin(urls[0], '/blobs/{}/{}'.format(hashalgo, blobhash))

    log.debug("posting file to %s", url)

    datagen, headers = poster.encode.multipart_encode({
        'data': open(filename, 'rb'),
        'filename': filename,
        'filesize': os.path.getsize(filename),
        'branch': branch,
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

    logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s",
                        level=loglevel)
    logging.getLogger('requests').setLevel(logging.WARN)

    for f in args['FILE']:
        if os.path.isfile(f):
            if args['--branch']:
                blob_id = upload_file(args['--url'], f, branch=args['--branch'])
            else:
                blob_id = upload_file(args['--url'], f)
            print f, blob_id

if __name__ == '__main__':
    main()
