import os
import unittest
import tempfile
import shutil
import time

from webtest import TestApp
from werkzeug.datastructures import ImmutableDict

from blobber.wsgi import app
from blobber.fs_plugin import FileBackend
from blobber.backend import BlobberBackend
from blobber.sqlalchemy_schema import Base
from sqlalchemy import create_engine
from bottle.ext import sqlalchemy as sqlalchemy_ext

class _BaseTest(unittest.TestCase):
    # initial needs for metadata database
    cur_path = os.path.dirname(os.path.abspath(__file__))
    metadb_name = "test_metadata.db"
    engine = create_engine("sqlite:////{path}/{name}".format(path=cur_path,
                                                             name=metadb_name))
    plugin = sqlalchemy_ext.Plugin(
        engine,
        Base.metadata,
        keyword="meta_db",
        create=True,
        commit=True,
        use_kwargs=False,
    )

    MOCK_OBJECTS = {
        "text_file": ImmutableDict({
            "filename": "files/text_file",
            "filesize": 3749,
            "branch": "branch-input",
            "mimetype": "application/octet-stream",
        }),

        "image": ImmutableDict({
            "filename": "files/Mozilla.jpg",
            "filesize": 36565,
            "branch": "branch-input",
            "mimetype": "application/octet-stream",
        }),

        "stackdump": ImmutableDict({
            "filename": "files/core",
            "filesize": 233472,
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
        B.files = FileBackend({"DIR": dir_testpath})
        app.backend = B

        # redo database for each set
        if _BaseTest.plugin in app.plugins:
            app.uninstall(_BaseTest.plugin)
            _BaseTest.engine = create_engine("sqlite:////{path}/{name}".format(path=_BaseTest.cur_path,
                                                                          name=_BaseTest.metadb_name))
            _BaseTest.plugin = sqlalchemy_ext.Plugin(
                _BaseTest.engine,
                Base.metadata,
                keyword="meta_db",
                create=True,
                commit=True,
                use_kwargs=False,
            )

        app.install(_BaseTest.plugin)

        self.app = TestApp(app)

    def tearDown(self):
        # delete actual data database
        shutil.rmtree(self.tempdir)
        # delete metadata database
        metadb_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   _BaseTest.metadb_name)
        os.remove(metadb_file)
