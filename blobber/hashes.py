import hashlib
from functools import partial

from blobber.async import sleep


def filehash(filename, hashalgo):
    h = hashlib.new(hashalgo)
    with open(filename, 'rb') as f:
        for block in iter(partial(f.read, 1024 ** 2), ''):
            h.update(block)
            # sleep()
    return h.hexdigest()

sha1sum = partial(filehash, hashalgo='sha1')
