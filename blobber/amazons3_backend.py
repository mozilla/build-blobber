from boto.s3.connection import S3Connection

from config import S3_BUCKET


def upload_to_AmazonS3(hashalgo, blobhash, data_file, headers, metadata):
    with open(data_file, "r") as fd:
        conn = S3Connection()
        bucket = conn.get_bucket(S3_BUCKET)

        _key = "blobs/%s/%s/%s" % (metadata['branch'], hashalgo, blobhash)
        key = bucket.new_key(_key)

        key.update_metadata(metadata)
        key.set_contents_from_file(fd, headers=headers)
        key.set_acl('public-read')

