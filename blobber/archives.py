import tempfile
import gzip
import bz2
import os

import sh
import magic


def get_archive_type(filename):
    type_ = magic.from_file(filename, mime=True)
    if type_ == 'application/zip':
        return 'zip'
    elif type_ == 'application/x-tar':
        return 'tar'
    elif type_ == "application/x-gzip":
        # Read a bit of the file and see if things look better
        header = gzip.open(filename, 'rb').read(1024)
        sub_type = magic.from_buffer(header, mime=True)
        if sub_type == 'application/x-tar':
            return 'tar'
    elif type_ == "application/x-bzip2":
        # Read a bit of the file and see if things look better
        header = bz2.BZ2File(filename, 'rb').read(1024)
        sub_type = magic.from_buffer(header, mime=True)
        if sub_type == 'application/x-tar':
            return 'tar'
    return None


def unpack_archive(filename, d=None):
    """Unpacks archive `filename` into `d` if set, otherwise into a tmpdir.
    Returns directory archive was unpacked into."""
    archive_type = get_archive_type(filename)
    if not archive_type:
        raise ValueError("Unknown archive type for %s" % filename)

    if d is None:
        d = tempfile.mkdtemp()

    filename = os.path.abspath(filename)

    if archive_type == "zip":
        sh.unzip("-q", filename, _cwd=d)
    elif archive_type == "tar":
        sh.tar("xf", filename, _cwd=d)
    else:
        raise ValueError("Unhandled archive type %s for filename %s" % (archive_type, filename))

    return d
