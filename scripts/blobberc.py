#!/usr/bin/env python
"""Usage: blobberc.py -u URL... -b BRANCH [-v] [-d] FILE

-u, --url URL          URL to blobber server to upload to.
-b, --branch BRANCH    Specify branch for the file (e.g. try, mozilla-central)
-v, --verbose          Increase verbosity
-d, --dir              Instead of a file, upload multiple files from a dir name

FILE                   Local file(s) to upload
"""
import urlparse
import os
import urllib2
import hashlib
import requests
import poster.encode
import logging
log = logging.getLogger(__name__)

from functools import partial

def filehash(filename, hashalgo):
    h = hashlib.new(hashalgo)
    with open(filename, 'rb') as f:
        for block in iter(partial(f.read, 1024 ** 2), ''):
            h.update(block)
    return h.hexdigest()

sha1sum = partial(filehash, hashalgo='sha1')

def upload_file(urls, filename, branch, hashalgo='sha1', blobhash=None):

    if blobhash is None:
        blobhash = filehash(filename, hashalgo)

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

def upload_dir(urls, dirname, branch, hashalgo='sha1'):
    log.info("opening the directory to read files")
    dir_files = [f for f in os.listdir(dirname)
                 if os.path.isfile(os.path.join(dirname, f))]

    log.info("Go through each file up upload to server")
    for f in dir_files:
        filename = os.path.join(dirname, f)
        log.info("Uploading %s", filename)
        upload_file(urls, filename, branch)
    log.info("Directory files uploaded successfully.")

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

    if args['--dir']:
        if os.path.isdir(args['FILE']):
            upload_dir(args['--url'], args['FILE'], branch=args['--branch'])
    else:
        if os.path.isfile(args['FILE']):
            upload_file(args['--url'], args['FILE'], branch=args['--branch'])

if __name__ == '__main__':
    main()
