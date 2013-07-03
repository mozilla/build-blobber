import os
import unittest
import tempfile
import shutil
import time
from webtest import TestApp
from werkzeug.datastructures import ImmutableDict

from blobber.wsgi import app
from blobber.fs_plugin import FileBackend
from blobber.backend import BlobberBackend, MissingBlobsError
from blobber.sqlite_plugin import MetadataBackend

class _BaseTest(unittest.TestCase):

    MOCK_OBJECTS = {
        "text_file": ImmutableDict({
            "filename": "files/text_file",
            "filesize": "3749",
            "branch": "branch-input",
            "mimetype": "application/octet-stream",
        }),

        "image": ImmutableDict({
            "filename": "files/Mozilla.jpg",
            "filesize": "36565",
            "branch": "branch-input",
            "mimetype": "application/octet-stream",
        }),

        "stackdump": ImmutableDict({
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
