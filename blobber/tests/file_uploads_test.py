import hashlib
import random
from collections import OrderedDict

from common import _BaseTest
from blobber.hashes import filehash, stringhash

class UploadFileTest(_BaseTest):

    def test_file_upload_with_text_file(self):

        _file_dict = self.MOCK_OBJECTS["text_file"]

        # post the file on wsgi server side
        file_hash = filehash(_file_dict['filename'], 'sha1')
        ret = self.app.post("/blobs/sha1/%s" % file_hash,
                            OrderedDict([(k,v) for k, v in _file_dict.items()]),
                            upload_files=[("data", _file_dict['filename'])],
                            status="*",
                            extra_environ={"REMOTE_ADDR": "127.0.0.1"},
                            )
        self.assertEqual(ret.status_code, 202)

        # get file from wsgi server side
        ret = self.app.get("/blobs/sha1/%s" % file_hash)
        self.assertEqual(ret.status_code, 200)

        # make sure the files are the same
        check_hash = stringhash(ret.body, 'sha1')
        self.assertEqual(file_hash, check_hash)

    def test_file_upload_with_image(self):

        _file_dict = self.MOCK_OBJECTS["image"]

        # post the file on wsgi server side
        file_hash = filehash(_file_dict['filename'], 'sha1')
        ret = self.app.post("/blobs/sha1/%s" % file_hash,
                            OrderedDict([(k,v) for k, v in _file_dict.items()]),
                            upload_files=[("data", _file_dict['filename'])],
                            status="*",
                            extra_environ={"REMOTE_ADDR": "127.0.0.1"},
                            )
        self.assertEqual(ret.status_code, 202)

        # get file from wsgi server side
        ret = self.app.get("/blobs/sha1/%s" % file_hash)
        self.assertEqual(ret.status_code, 200)

        # make sure the files are the same
        check_hash = stringhash(ret.body, 'sha1')
        self.assertEqual(file_hash, check_hash)

    def test_file_upload_with_stackdump(self):

        _file_dict = self.MOCK_OBJECTS["stackdump"]

        # post the file on wsgi server side
        file_hash = filehash(_file_dict['filename'], 'sha1')
        ret = self.app.post("/blobs/sha1/%s" % file_hash,
                            OrderedDict([(k,v) for k, v in _file_dict.items()]),
                            upload_files=[("data", _file_dict['filename'])],
                            status="*",
                            extra_environ={"REMOTE_ADDR": "127.0.0.1"},
                            )
        self.assertEqual(ret.status_code, 202)

        # get file from wsgi server side
        ret = self.app.get("/blobs/sha1/%s" % file_hash)
        self.assertEqual(ret.status_code, 200)

        # make sure the files are the same
        check_hash = stringhash(ret.body, 'sha1')
        self.assertEqual(file_hash, check_hash)

    def test_file_upload_with_extra_arguments_for_text_file(self):

        _file_dict = self.MOCK_OBJECTS["text_file"]

        # post the file on wsgi server side
        file_hash = filehash(_file_dict['filename'], 'sha1')

        wrong_dict = {'extra_argument': 'do not add me in the database'}
        wrong_dict.update({k:v for k, v in _file_dict.items()})

        ret = self.app.post("/blobs/sha1/%s" % file_hash,
                            OrderedDict([(k,v) for k, v in wrong_dict.items()]),
                            upload_files=[("data", _file_dict['filename'])],
                            extra_environ={"REMOTE_ADDR": "127.0.0.1"},
                            status="*")
        # make sure no error page is returned from server
        self.assertEqual(ret.status_code, 202)

        # get file from wsgi server side
        ret = self.app.get("/blobs/sha1/%s" % file_hash)
        self.assertEqual(ret.status_code, 200)

        # make sure the files are the same
        check_hash = stringhash(ret.body, 'sha1')
        self.assertEqual(file_hash, check_hash)

    def test_file_upload_with_extra_arguments_for_image(self):

        _file_dict = self.MOCK_OBJECTS["image"]

        # post the file on wsgi server side
        file_hash = filehash(_file_dict['filename'], 'sha1')

        wrong_dict = {'extra_argument': 'do not add me in the database'}
        wrong_dict.update({k:v for k, v in _file_dict.items()})

        ret = self.app.post("/blobs/sha1/%s" % file_hash,
                            OrderedDict([(k,v) for k, v in wrong_dict.items()]),
                            upload_files=[("data", _file_dict['filename'])],
                            extra_environ={"REMOTE_ADDR": "127.0.0.1"},
                            status="*")
        # make sure no error page is returned from server
        self.assertEqual(ret.status_code, 202)

        # get file from wsgi server side
        ret = self.app.get("/blobs/sha1/%s" % file_hash)
        self.assertEqual(ret.status_code, 200)

        # make sure the files are the same
        check_hash = stringhash(ret.body, 'sha1')
        self.assertEqual(file_hash, check_hash)

    def test_file_upload_with_extra_arguments_for_stackdump(self):

        _file_dict = self.MOCK_OBJECTS["stackdump"]

        # post the file on wsgi server side
        file_hash = filehash(_file_dict['filename'], 'sha1')

        wrong_dict = {'extra_argument': 'do not add me in the database'}
        wrong_dict.update({k:v for k, v in _file_dict.items()})

        ret = self.app.post("/blobs/sha1/%s" % file_hash,
                            OrderedDict([(k,v) for k, v in wrong_dict.items()]),
                            upload_files=[("data", _file_dict['filename'])],
                            extra_environ={"REMOTE_ADDR": "127.0.0.1"},
                            status="*")
        # make sure no error page is returned from server
        self.assertEqual(ret.status_code, 202)

        # get file from wsgi server side
        ret = self.app.get("/blobs/sha1/%s" % file_hash)
        self.assertEqual(ret.status_code, 200)

        # make sure the files are the same
        check_hash = stringhash(ret.body, 'sha1')
        self.assertEqual(file_hash, check_hash)

    def test_file_upload_with_less_arguments_for_text_file(self):

        _file_dict = self.MOCK_OBJECTS["text_file"]
        # post the file on wsgi server side
        file_hash = filehash(_file_dict['filename'], 'sha1')

        wrong_dict = {k:v for k, v in _file_dict.items()}
        # delete random key from dictionary
        del wrong_dict[random.choice(wrong_dict.keys())]

        ret = self.app.post("/blobs/sha1/%s" % file_hash,
                            OrderedDict([(k,v) for k, v in wrong_dict.items()]),
                            upload_files=[("data", _file_dict['filename'])],
                            extra_environ={"REMOTE_ADDR": "127.0.0.1"},
                            status="*")
        # make sure no success page is returned from server
        self.assertEqual(ret.status_code, 400)

    def test_file_upload_with_less_arguments_for_image(self):

        _file_dict = self.MOCK_OBJECTS["image"]
        # post the file on wsgi server side
        file_hash = filehash(_file_dict['filename'], 'sha1')

        wrong_dict = {k:v for k, v in _file_dict.items()}
        # delete random key from dictionary
        del wrong_dict[random.choice(wrong_dict.keys())]

        ret = self.app.post("/blobs/sha1/%s" % file_hash,
                            OrderedDict([(k,v) for k, v in wrong_dict.items()]),
                            upload_files=[("data", _file_dict['filename'])],
                            extra_environ={"REMOTE_ADDR": "127.0.0.1"},
                            status="*")
        # make sure no success page is returned from server
        self.assertEqual(ret.status_code, 400)

    def test_file_upload_with_less_arguments_for_stackdump(self):

        _file_dict = self.MOCK_OBJECTS["stackdump"]
        # post the file on wsgi server side
        file_hash = filehash(_file_dict['filename'], 'sha1')

        wrong_dict = {k:v for k, v in _file_dict.items()}
        # delete random key from dictionary
        del wrong_dict[random.choice(wrong_dict.keys())]

        ret = self.app.post("/blobs/sha1/%s" % file_hash,
                            OrderedDict([(k,v) for k, v in wrong_dict.items()]),
                            upload_files=[("data", _file_dict['filename'])],
                            extra_environ={"REMOTE_ADDR": "127.0.0.1"},
                            status="*")
        # make sure no success page is returned from server
        self.assertEqual(ret.status_code, 400)
