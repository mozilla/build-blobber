import hashlib
from collections import OrderedDict

from common import _BaseTest
from blobber.hashes import filehash, stringhash

class UploadFileTest(_BaseTest):

    def test_file_upload(self):

        for file_type, _file_dict in self.MOCK_OBJECTS.items():
            # post the file on wsgi server side
            file_hash = filehash(_file_dict['filename'], 'sha1')
            ret = self.app.post("/blobs/sha1/%s" % file_hash,
                                OrderedDict([(k,v) for k, v in _file_dict.items()]),
                                upload_files=[("data", _file_dict['filename'])],
                                status="*")
            self.assertEqual(ret.status_code, 202)

            # get file from wsgi server side
            ret = self.app.get("/blobs/sha1/%s" % file_hash)
            self.assertEqual(ret.status_code, 200)

            # make sure the files are the same
            # TODO - reading in blocks to avoid in-memory exceeding
            check_hash = stringhash(ret.body, 'sha1')
            self.assertEqual(file_hash, check_hash)

