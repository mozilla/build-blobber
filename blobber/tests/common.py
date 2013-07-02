import unittest
import tempfile
import shutil
from webtest import TestApp

from blobber.wsgi import app
from blobber.fs_plugin import FileBackend
from blobber.backend import BlobberBackend, MissingBlobsError

class _BaseTest(unittest.TestCase):

    TESTING_FILES = {
        "text_file": "files/text_file",
        "image": "files/Mozilla.jpg",
        "stackdump": "files/core",
        "bad_data": "files/bad_data",
    }

    def setUp(self):
        B = BlobberBackend({})
        # get a temporary file directory in /tmp
        self.tempdir = tempfile.mkdtemp()
        # create subfolder for testing evn use
        dir_testpath = tempfile.mkdtemp(suffix='store',
                                        prefix='file_',
                                        dir=self.tempdir)

        B.files = FileBackend({"dir": dir_testpath})
        app.backend = B

        self.app = TestApp(app)

    def tearDown(self):
        shutil.rmtree(self.tempdir)
