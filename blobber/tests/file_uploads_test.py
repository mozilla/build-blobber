import hashlib

from common import _BaseTest
from blobber.hashes import filehash, stringhash

class UploadFileTest(_BaseTest):

    def test_file_upload(self):

        for file_type, _file in self.TESTING_FILES.items():
            # post the file on wsgi server side
            file_hash = filehash(_file, 'sha1')
            ret = self.app.post("/blobs/sha1/%s" % file_hash,
                                upload_files=[("data", _file)],
                                status="*")
            self.assertEqual(ret.status_code, 202)

            # get file from wsgi server side
            ret = self.app.get("/blobs/sha1/%s" % file_hash)
            self.assertEqual(ret.status_code, 200)

            # make sure the files are the same
            check_hash = stringhash(ret.body, 'sha1')
            self.assertEqual(file_hash, check_hash)

