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
    datagen, headers = poster.encode.multipart_encode({'data': open(filename, 'rb')})
    req = urllib2.Request(url, datagen, headers)
    urllib2.urlopen(req)


def upload_dir(urls, dirname):
    log.info("creating manifest for %s", dirname)
    manifest = blobber.manifest.make_manifest(dirname)

    files_by_hash = dict(((e.hashalgo, e.hash), e.path) for e in manifest['entries'] if e.type == blobber.manifest.FILE)

    # Shuffle the urls
    urls = urls[:]
    random.shuffle(urls)

    # Upload the manifest, get list of missing objects, upload objects, repeat
    while True:
        url = urlparse.urljoin(urls[0], '/manifests')

        log.info("posting manifest to %s", url)
        response = requests.post(url, data=blobber.manifest.to_json(manifest), headers={'Content-Type': 'application/json'})
        response_js = response.json()
        if response.status_code == 202:
            return response_js
        if 'missing_blobs' in response_js:
            log.info("uploading missing blobs")
            # TODO: do this concurrently
            for m in response_js['missing_blobs']:
                # Manifest paths always start with /, so strip that off for the
                # join
                filename = os.path.join(dirname, files_by_hash[tuple(m)][1:])
                log.debug("Uploading %s", filename)
                upload_file(urls, filename, hashalgo=m[0], blobhash=m[1])


def upload_archive(urls, filename):
    log.info("unpacking %s", filename)
    d = blobber.archives.unpack_archive(filename)
    try:
        return upload_dir(urls, d)
    finally:
        shutil.rmtree(d)


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
        if args['--unpack-archives']:
            manifest_id = upload_archive(args['--url'], f)
            print f, manifest_id
        elif os.path.isfile(f):
            blob_id = upload_file(args['--url'], f, check_first=False)
            print f, blob_id
        elif os.path.isdir(f):
            manifest_id = upload_dir(args['--url'], f)
            print f, manifest_id

if __name__ == '__main__':
    main()
