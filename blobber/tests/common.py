import unittest
from webtest import TestApp

from blobber.wsgi import app
from blobber.fs_plugin import FileBackend
from blobber.backend import BlobberBackend, MissingBlobsError

class _BaseTest(unittest.TestCase):

    TESTING_FILES = {
        "text_file": "files/text_file",
        "image": "files/Mozilla.jpg",
        "stackdump": "files/core"
    }

    def setUp(self):
        B = BlobberBackend({})
        B.files = FileBackend({"dir": "file_store"})
        app.backend = B

        self.app = TestApp(app)

    def tearDown(self):
        pass
