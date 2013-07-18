import hashlib
from functools import partial

def stringhash(stringobj, hashalgo):
    h = hashlib.new(hashalgo)
    h.update(stringobj)
    return h.hexdigest()


def filehash(filename, hashalgo):
    h = hashlib.new(hashalgo)
    with open(filename, 'rb') as f:
        for block in iter(partial(f.read, 1024 ** 2), ''):
            h.update(block)
    return h.hexdigest()

sha1sum = partial(filehash, hashalgo='sha1')
