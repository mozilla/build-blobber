import os
import unittest
import tempfile
import shutil
from webtest import TestApp
from werkzeug.datastructures import ImmutableDict
from datetime import datetime

from blobber.wsgi import app
from blobber.fs_plugin import FileBackend
from blobber.backend import BlobberBackend, MissingBlobsError
from blobber.sqlite_plugin import MetadataBackend

class _BaseTest(unittest.TestCase):

    MOCK_OBJECTS = {
        "text_file": ImmutableDict({
            "blobhash": "a1b563a685fc1f8e3eab78cbc941dc9a80507456",
            "upload_time": datetime.now(),
            "upload_ip": "127.0.0.1",
            "filename": "files/text_file",
            "filesize": "3749",
            "branch": "branch-input",
            "mimetype": "application/octet-stream",
        }),

        "image": ImmutableDict({
            "blobhash": "44464cab6ee4dc179bf8f0b52a2d1343c4e1ae9f",
            "upload_time": datetime.now(),
            "upload_ip": "127.0.0.1",
            "filename": "files/Mozilla.jpg",
            "filesize": "36565",
            "branch": "branch-input",
            "mimetype": "application/octet-stream",
        }),

        "stackdump": ImmutableDict({
            "blobhash": "c49e6fe7321f6db7f54582c41e82f4dbe2e472c8",
            "upload_time": datetime.now(),
            "upload_ip": "127.0.0.1",
            "filename": "files/core",
            "filesize": "233472",
            "branch": "branch-input",
            "mimetype": "application/octet-stream",
        }),

    }

    def setUp(self):
        # get a temporary file directory in /tmp
        self.tempdir = tempfile.mkdtemp()
        # create subfolder for testing evn use
        dir_testpath = tempfile.mkdtemp(suffix='store',
                                        prefix='file_',
                                        dir=self.tempdir)

        B = BlobberBackend({})
        B.files = FileBackend({"dir": dir_testpath})
        app.backend = B

        self.metadb_name = "testdatabase.db"
        metaB = MetadataBackend({"name": self.metadb_name})
        app.meta_backend = metaB

        self.app = TestApp(app)

    def tearDown(self):
        # delete actual data database
        shutil.rmtree(self.tempdir)
        # delete metadata database
        metadb_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              self.metadb_name)
        os.remove(metadb_file)
