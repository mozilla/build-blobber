import os
import json
from collections import namedtuple

from blobber.hashes import sha1sum

FileEntry = namedtuple('FileEntry', ['type', 'hashalgo', 'hash', 'size', 'path', 'mtime', 'mode'])
DirEntry = namedtuple('DirEntry', ['type', 'path', 'mtime', 'mode'])
FILE, DIR = 0, 1


def make_dir_entry(dirname, relpath=None):
    path = dirname
    if relpath:
        assert dirname.startswith(relpath)
        path = dirname[len(relpath):]
    return DirEntry(
        type=DIR,
        path=path,
        mtime=int(os.path.getmtime(dirname)),
        mode=os.stat(dirname).st_mode & 0o777,
    )


def make_file_entry(filename, relpath=None):
    path = filename
    if relpath:
        assert filename.startswith(relpath)
        path = filename[len(relpath):]
    return FileEntry(
        type=FILE,
        hashalgo='sha1',
        hash=sha1sum(filename),
        size=os.path.getsize(filename),
        path=path,
        mtime=(os.path.getmtime(filename)),
        mode=os.stat(filename).st_mode & 0o777,
    )


def make_manifest(dirname):
    """Returns a manifest that represents all the contents of dirname. A manifest is a list of Entry objects"""
    retval = []
    for root, dirs, files in os.walk(dirname):
        for d in dirs:
            full_d = os.path.join(root, d)
            e = make_dir_entry(full_d, relpath=dirname)
            retval.append(e)
        for f in files:
            full_f = os.path.join(root, f)
            e = make_file_entry(full_f, relpath=dirname)
            retval.append(e)

    return {'manifest_version': 1, 'entries': sorted(retval, key=lambda e: e.path)}


def to_json(manifest):
    return json.dumps(manifest, separators=',:')


def convert_manifest(manifest):
    """Converts tuples from a manifest dict into the namedtuples above"""
    new_entries = []
    for e in manifest['entries']:
        if e[0] == FILE:
            e = FileEntry(*e)
        elif e[0] == DIR:
            e = DirEntry(*e)
        else:
            raise ValueError("Unsupported entry type %s" % e[0])
        new_entries.append(e)
    manifest['entries'] = new_entries
